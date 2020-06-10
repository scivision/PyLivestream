import bisect
from pathlib import Path
import logging
import os
import sys
from configparser import ConfigParser
from typing import List

#
from . import utils
from .ffmpeg import Ffmpeg, get_exe

# %%  Col0: vertical pixels (height). Col1: video kbps. Interpolates.
# NOTE: Python >= 3.6 has guaranteed dict() order.
# YouTube spec: https://support.google.com/youtube/answer/2853702

BR30 = {240: 300, 360: 400, 480: 500, 720: 2500, 1080: 3000, 1440: 6000, 2160: 13000}

BR60 = {720: 2250, 1080: 4500, 1440: 9000, 2160: 20000}

# for static images, ignore YouTube bitrate warning as long as image looks OK on stream
BRS = {240: 200, 480: 400, 720: 800, 1080: 1200, 1440: 2000, 2160: 4000}

FPS: float = 30.0  # default frames/sec if not defined otherwise


# %% top level
class Stream:
    def __init__(self, inifn: Path, site: str, **kwargs):

        self.F = Ffmpeg()

        self.loglevel: List[str] = self.F.INFO if kwargs.get("verbose") else self.F.ERROR

        self.inifn: Path = Path(inifn).expanduser() if inifn else None

        self.site: str = site
        self.vidsource = kwargs.get("vidsource")

        if kwargs.get("image"):
            self.image = Path(kwargs["image"]).expanduser()
        else:
            self.image = None

        self.loop: bool = kwargs.get("loop")

        self.infn = Path(kwargs["infn"]).expanduser() if kwargs.get("infn") else None
        self.yes: List[str] = self.F.YES if kwargs.get("yes") else []

        self.queue: List[str] = []  # self.F.QUEUE

        self.caption: str = kwargs.get("caption")

        self.timelimit: List[str] = self.F.timelimit(kwargs.get("timeout"))

    def osparam(self, key: str):
        """load OS specific config"""

        C = ConfigParser(inline_comment_prefixes=("#", ";"))
        if self.inifn is None:
            logging.info("using package default pylivestream.ini")
            cfg = utils.get_inifile("pylivestream.ini")
        else:
            cfg = Path(self.inifn).expanduser().read_text()

        C.read_string(cfg)

        self.exe = get_exe(C.get(sys.platform, "exe", fallback="ffmpeg"))
        self.probeexe = get_exe(C.get(sys.platform, "ffprobe_exe", fallback="ffprobe"))

        if self.site not in C:
            raise ValueError(
                f"streaming site {self.site} not found in configuration file {self.inifn}"
            )

        if "XDG_SESSION_TYPE" in os.environ:
            if os.environ["XDG_SESSION_TYPE"] == "wayland":
                logging.error("Wayland may only give black output. Try X11")

        if self.vidsource == "camera":
            self.res: List[str] = C.get(self.site, "webcam_res").split("x")
            self.fps: float = C.getint(self.site, "webcam_fps")
            self.movingimage = self.staticimage = False
        elif self.vidsource == "screen":
            self.res = C.get(self.site, "screencap_res").split("x")
            self.fps = C.getint(self.site, "screencap_fps")
            self.origin: List[str] = C.get(self.site, "screencap_origin").split(",")
            self.movingimage = self.staticimage = False
        elif self.vidsource == "file":  # streaming video from a file
            self.res = utils.get_resolution(self.infn, self.probeexe)
            self.fps = utils.get_framerate(self.infn, self.probeexe)
        elif self.vidsource is None and self.image:  # audio-only stream + background image
            self.res = utils.get_resolution(self.image, self.probeexe)
            self.fps = utils.get_framerate(self.infn, self.probeexe)
        else:  # audio-only
            self.res = None
            self.fps = None

        if self.res is not None and len(self.res) != 2:
            raise ValueError(f"need height, width of video resolution, I have: {self.res}")

        self.audiofs: str = C.get(self.site, "audiofs")
        self.preset: str = C.get(self.site, "preset")

        if not self.timelimit:
            self.timelimit = self.F.timelimit(C.get(self.site, "timelimit", fallback=None))

        # NOTE: This used to be 'videochan' but that was too generic.
        self.webcamchan: str = C.get(sys.platform, "webcamchan", fallback=None)
        self.screenchan: str = C.get(sys.platform, "screenchan", fallback=None)

        self.audiochan: str = C.get(sys.platform, "audiochan", fallback=None)

        self.vcap: str = C.get(sys.platform, "vcap")
        self.acap: str = C.get(sys.platform, "acap", fallback=None)

        self.hcam: str = C.get(sys.platform, "hcam")

        self.video_kbps: int = C.getint(self.site, "video_kbps", fallback=None)
        self.audio_bps: str = C.get(self.site, "audio_bps")

        self.keyframe_sec: int = C.getint(self.site, "keyframe_sec")

        self.server: str = C.get(self.site, "server", fallback=None)
        # %% Key (hexaecimal stream ID)
        if key:
            self.key: str = utils.getstreamkey(key)
        else:
            self.key = utils.getstreamkey(C.get(self.site, "key", fallback=None))

    def videoIn(self, quick: bool = False) -> List[str]:
        """
        config video input
        """

        if self.vidsource == "screen":
            v = self.screengrab(quick)
        elif self.vidsource == "camera":
            v = self.webcam(quick)
        elif self.vidsource is None or self.vidsource == "file":
            v = self.filein(quick)
        else:
            raise ValueError(f"unknown vidsource {self.vidsource}")

        if sys.platform == "darwin":
            v = ["-pix_fmt", "uyvy422"] + v

        return v

    def videoOut(self) -> List[str]:
        """
        configure video output
        """

        vid_format = "uyvy422" if sys.platform == "darwin" else "yuv420p"
        v: List[str] = ["-codec:v", "libx264", "-pix_fmt", vid_format]
        # %% set frames/sec, bitrate and keyframe interval
        """
         DON'T DO THIS.
         It makes keyframes/bitrate far off from what streaming sites want
         v += ['-tune', 'stillimage']

         The settings below still save video/data bandwidth for the still image
         + audio case.
        """
        if self.res is None:  # audio-only, no image or video
            return []

        fps = self.fps if self.fps is not None else FPS

        v += ["-preset", self.preset, "-b:v", str(self.video_kbps) + "k"]

        if self.image:
            v += ["-r", str(fps)]

        v += ["-g", str(self.keyframe_sec * fps)]

        return v

    def audioIn(self, quick: bool = False) -> List[str]:
        """
        -ac 2 doesn't seem to be needed, so it was removed.

        NOTE: -ac 2 NOT -ac 1 to avoid "non monotonous DTS in output stream" errors
        """
        if not (self.audio_bps and self.acap and self.audiochan and self.audiofs):
            return []

        if self.audiochan == "null" or self.acap == "null":
            self.acap = "null"
            if not self.audio_bps:
                self.audio_bps = "128000"
            if not self.audiofs:
                self.audiofs = "48000"
            self.audiochan = f"anullsrc=sample_rate={self.audiofs}:channel_layout=stereo"

        if self.vidsource == "file":
            a: List[str] = []
        elif self.acap == "null":
            a = ["-f", "lavfi", "-i", self.audiochan]
        else:
            a = ["-f", self.acap, "-i", self.audiochan]

        return a

    def audioOut(self) -> List[str]:
        """
        select audio codec

        https://trac.ffmpeg.org/wiki/Encode/AAC#FAQ
        https://support.google.com/youtube/answer/2853702?hl=en
        https://www.facebook.com/facebookmedia/get-started/live
        """

        if not (self.audio_bps and self.acap and self.audiochan and self.audiofs):
            return []

        return ["-codec:a", "aac", "-b:a", str(self.audio_bps), "-ar", str(self.audiofs)]

    def video_bitrate(self):
        """
        get "best" video bitrate.
        Based on YouTube Live minimum specified stream rate.
        """
        if self.video_kbps:  # per-site override
            return

        if self.res is not None:
            x: int = int(self.res[1])
        elif self.vidsource is None or self.vidsource == "file":
            logging.info("assuming 480p input.")
            x = 480
        else:
            raise ValueError(
                "Unsure of your video resolution request."
                "Try setting video_kpbs in PyLivestream configuration file (see README.md)"
            )

        if self.fps is None or self.fps < 20:
            self.video_kbps: int = list(BRS.values())[bisect.bisect_left(list(BRS.keys()), x)]
        elif 20 <= self.fps <= 35:
            self.video_kbps: int = list(BR30.values())[bisect.bisect_left(list(BR30.keys()), x)]
        else:
            self.video_kbps: int = list(BR60.values())[bisect.bisect_left(list(BR60.keys()), x)]

    def screengrab(self, quick: bool = False) -> List[str]:
        """
        grab video from desktop.
        May not work for Wayland desktop.
        """

        v: List[str] = ["-f", self.vcap]

        # FIXME: explict frame rate is problematic for MacOS with screenshare. Just leave it off?
        # if not quick:
        #     v += ['-r', str(self.fps)]

        if not quick and self.res is not None:
            v += ["-s", "x".join(map(str, self.res))]

        if sys.platform == "linux":
            if quick:
                v += ["-i", self.screenchan]
            else:
                v += ["-i", f"{self.screenchan}+{self.origin[0]},{self.origin[1]}"]
        elif sys.platform == "win32":
            if not quick:
                v += ["-offset_x", str(self.origin[0]), "-offset_y", str(self.origin[1])]

            v += ["-i", self.screenchan]

        elif sys.platform == "darwin":
            v += ["-i", self.screenchan]

        return v

    def webcam(self, quick: bool = False) -> List[str]:
        """
        configure webcam

        https://trac.ffmpeg.org/wiki/Capture/Webcam
        """
        webcam_chan = self.webcamchan

        if sys.platform == "darwin":
            if not webcam_chan:
                webcam_chan = "default"

        v: List[str] = ["-f", self.hcam, "-i", webcam_chan]

        #  '-r', str(self.fps),  # -r causes bad dropouts

        return v

    def filein(self, quick: bool = False) -> List[str]:
        """
        used for:

        * stream input file  (video, or audio + image)
        * microphone-only
        """

        v: List[str] = []

        """
        -re is NOT for actual streaming devices (webcam, microphone)
        https://ffmpeg.org/ffmpeg.html
        """
        # assumes GIF is animated
        if isinstance(self.image, Path):
            self.movingimage = self.image.suffix in (".gif", ".avi", ".ogv", ".mp4")
            self.staticimage = not self.movingimage
        else:
            self.movingimage = self.staticimage = False
        # %% throttle software-only sources
        if (self.vidsource is not None and self.image) or self.vidsource == "file":
            v.append(self.F.THROTTLE)
        # %% image /  audio / vidoe cases
        if self.staticimage:
            if not quick:
                v += ["-loop", "1"]
            v.extend(["-f", "image2", "-i", str(self.image)])
        elif self.movingimage:
            v.extend(self.F.movingBG(self.image))
        elif self.loop and not self.image:  # loop for traditional video
            if not quick:
                v.extend(["-stream_loop", "-1"])  # FFmpeg >= 3
        # %% audio (for image+audio) or video
        if self.infn:
            v.extend(["-i", str(self.infn)])

        return v

    def buffer(self, server: str) -> List[str]:
        """configure network buffer. Tradeoff: latency vs. robustness"""
        # constrain to single thread, default is multi-thread
        # buf = ['-threads', '1']

        buf = ["-maxrate", f"{self.video_kbps}k", "-bufsize", f"{self.video_kbps//2}k"]

        if self.staticimage:  # static image + audio
            buf += ["-shortest"]

        # for very old versions of FFmpeg, such as Ubuntu 16.04
        # still OK for current FFmpeg versions too
        buf += ["-strict", "experimental"]

        # must manually specify container format when streaming to web.
        buf += ["-f", "flv"]

        return buf
