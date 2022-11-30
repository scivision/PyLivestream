from __future__ import annotations
import bisect
from pathlib import Path
import logging
import os
import sys
import json

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

        self.loglevel: list[str] = self.F.INFO if kwargs.get("verbose") else self.F.ERROR

        self.inifn: Path = Path(inifn).expanduser().resolve(strict=True)

        self.site: str = site
        self.vidsource = kwargs.get("vidsource")

        if kwargs.get("image"):
            self.image = Path(kwargs["image"]).expanduser()
        else:
            self.image = None

        self.loop: bool = kwargs.get("loop")

        self.infn = Path(kwargs["infn"]).expanduser() if kwargs.get("infn") else None
        self.yes: list[str] = self.F.YES if kwargs.get("yes") else []

        self.queue: list[str] = []  # self.F.QUEUE

        self.caption: str = kwargs.get("caption")

        self.timelimit: list[str] = self.F.timelimit(kwargs.get("timeout"))

    def osparam(self, fn: Path) -> None:
        """load OS specific config"""

        fn = Path(fn).expanduser().resolve(strict=True)

        C = json.loads(fn.read_text())

        try:
            syscfg = C[sys.platform]
        except KeyError:
            raise KeyError(f"No system config {sys.platform} in {fn}")

        self.json_file = fn

        self.exe = get_exe(C.get("exe", "ffmpeg"))
        self.probeexe = get_exe(C.get("ffprobe_exe", "ffprobe"))

        if "XDG_SESSION_TYPE" in os.environ:
            if os.environ["XDG_SESSION_TYPE"] == "wayland":
                logging.error("Wayland may only give black output. Try X11")

        try:
            sitecfg = C["sites"][self.site]
        except KeyError:
            raise KeyError(f"No config sites: {self.site} in {fn}")

        if self.vidsource == "camera":
            self.res: list[str] = C.get("camera_size")
            self.fps: float = C.get("camera_fps")
            self.movingimage = self.staticimage = False
        elif self.vidsource == "screen":
            self.res = C.get("screencap_size")
            self.fps = C.get("screencap_fps")
            self.origin: list[str] = C.get("screencap_origin", [1, 1])
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

        self.audio_rate: str = C.get("audio_rate")
        self.preset: str = C.get("preset")

        if not self.timelimit:
            self.timelimit = self.F.timelimit(sitecfg.get("timelimit"))

        self.camera_chan: str = syscfg.get("camera_chan")
        self.screen_chan: str = syscfg.get("screen_chan")

        self.audio_chan: str = syscfg.get("audio_chan")

        self.vcap: str = syscfg.get("vcap")
        self.acap: str = syscfg.get("acap")

        self.hcam: str = syscfg.get("hcam")

        self.video_kbps: int = sitecfg.get("video_kbps")
        self.audio_bps: str = sitecfg.get("audio_bps")

        self.keyframe_sec: int = sitecfg.get("keyframe_sec")

        self.url: str = sitecfg.get("url")
        self.streamid: str = sitecfg.get("streamid", "")

    def videoIn(self, quick: bool = False) -> list[str]:
        """
        config video input
        """

        if self.vidsource == "screen":
            v = self.screengrab(quick)
            if sys.platform == "darwin":
                # not for files "option pixel_format not found"
                v = ["-pix_fmt", "uyvy422"] + v
        elif self.vidsource == "camera":
            v = self.camera(quick)
            if sys.platform == "darwin":
                # not for files "option pixel_format not found"
                v = ["-pix_fmt", "uyvy422"] + v
        elif self.vidsource is None or self.vidsource == "file":
            v = self.filein(quick)
        else:
            raise ValueError(f"unknown vidsource {self.vidsource}")

        return v

    def videoOut(self) -> list[str]:
        """
        configure video output
        """

        vid_format = "uyvy422" if sys.platform == "darwin" else "yuv420p"
        v: list[str] = ["-codec:v", "libx264", "-pix_fmt", vid_format]
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

    def audioIn(self, quick: bool = False) -> list[str]:
        """
        -ac 2 doesn't seem to be needed, so it was removed.

        NOTE: -ac 2 NOT -ac 1 to avoid "non monotonous DTS in output stream" errors
        """

        if not (self.audio_bps and self.acap and self.audio_chan and self.audio_rate):
            return []

        if self.audio_chan == "null" or self.acap == "null":
            self.acap = "null"
            if not self.audio_bps:
                self.audio_bps = "128000"
            if not self.audio_rate:
                self.audio_rate = "48000"
            self.audio_chan = f"anullsrc=sample_rate={self.audio_rate}:channel_layout=stereo"

        if self.vidsource == "file":
            a: list[str] = []
        elif self.acap == "null":
            a = ["-f", "lavfi", "-i", self.audio_chan]
        else:
            a = ["-f", self.acap, "-i", self.audio_chan]

        return a

    def audioOut(self) -> list[str]:
        """
        select audio codec

        https://trac.ffmpeg.org/wiki/Encode/AAC#FAQ
        https://support.google.com/youtube/answer/2853702?hl=en
        https://www.facebook.com/facebookmedia/get-started/live
        """

        if not (self.audio_bps and self.acap and self.audio_chan and self.audio_rate):
            return []

        return ["-codec:a", "aac", "-b:a", str(self.audio_bps), "-ar", str(self.audio_rate)]

    def video_bitrate(self) -> None:
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
                """
Unsure of your video resolution request.
Try setting video_kpbs in pylivestream.json file (see README.md)
"""
            )

        if self.fps is None or self.fps < 20:
            k = BRS.keys()
            v = BRS.values()
        elif 20 <= self.fps <= 35:
            k = BR30.keys()
            v = BR30.values()
        else:
            k = BR60.keys()
            v = BR60.values()

        self.video_kbps: int = list(v)[bisect.bisect_left(list(k), x)]  # type: ignore  # allow redef mypy bug?

    def screengrab(self, quick: bool = False) -> list[str]:
        """
        grab video from desktop.
        May not work for Wayland desktop.
        """

        v = ["-f", self.vcap]

        # FIXME: explict frame rate is problematic for MacOS with screenshare. Just leave it off?
        # if not quick:
        #     v += ['-r', str(self.fps)]

        if not quick and self.res is not None:
            v += ["-s", "x".join(map(str, self.res))]

        if sys.platform == "linux":
            if quick:
                v += ["-i", self.screen_chan]
            else:
                v += ["-i", f"{self.screen_chan}+{self.origin[0]},{self.origin[1]}"]
        elif sys.platform == "win32":
            if not quick:
                v += ["-offset_x", str(self.origin[0]), "-offset_y", str(self.origin[1])]

            v += ["-i", self.screen_chan]

        elif sys.platform == "darwin":
            v += ["-i", self.screen_chan]

        return v

    def camera(self, quick: bool = False) -> list[str]:
        """
        configure camera

        https://trac.ffmpeg.org/wiki/Capture/Webcam
        """

        c = self.camera_chan

        if sys.platform == "darwin":
            if not c:
                c = "default"

        v = ["-f", self.hcam, "-i", c]

        #  '-r', str(self.fps),  # -r causes bad dropouts

        return v

    def filein(self, quick: bool = False) -> list[str]:
        """
        used for:

        * stream input file  (video, or audio + image)
        * microphone-only
        """

        v: list[str] = []

        """
        -re is NOT for actual streaming devices (camera, microphone)
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

    def buffer(self) -> list[str]:
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
