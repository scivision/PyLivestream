import bisect
from pathlib import Path
import logging
import os
import sys
from configparser import ConfigParser
from typing import Tuple, List, Dict
#
from . import sio

# %%  Col0: vertical pixels (height). Col1: video kbps. Interpolates.
# NOTE: Python >= 3.6 has guaranteed dict() order.

BR30 = dict([
        (240, 300),
        (360, 400),
        (480, 500),
        (540, 800),
        (720, 1800),
        (1080, 3000),
        (1440, 6000),
        (2160, 13000)])

BR60 = dict([
       (720, 2250),
       (1080, 4500),
       (1440, 9000),
       (2160, 20000)])

FPS = 30.  # default frames/sec if not defined otherwise


# %% top level
class Stream:

    def __init__(self, ini: Path, site: str, vidsource: str=None,
                 image: Path=None, loop: bool=False, infn: Path=None,
                 yes: bool=False) -> None:

        self.ini: Path = Path(ini).expanduser()
        self.site: str = site
        self.vidsource = vidsource
        self.image = Path(image).expanduser() if image else None
        self.loop = loop

        self.infn = Path(infn).expanduser() if infn else None
        self.yes = yes

    def osparam(self):
        """load OS specific config"""

        assert self.ini.is_file(), f'{self.ini} not found.'

        C = ConfigParser(inline_comment_prefixes=('#', ';'))
        C.read(str(self.ini))

        assert self.site in C, f'{self.site} not found: {self.ini}'

        if 'XDG_SESSION_TYPE' in os.environ:
            if os.environ['XDG_SESSION_TYPE'] == 'wayland':
                logging.error('Wayland may only give black output. Try X11')

        self.exe, self.probeexe = sio.getexe(C.get(sys.platform, 'exe',
                                                   fallback='ffmpeg'))

        if self.vidsource == 'camera':
            self.res: Tuple[int, int] = C.get(self.site,
                                              'webcam_res').split('x')
            self.fps: float = C.getint(self.site, 'webcam_fps')
        elif self.vidsource == 'screen':
            self.res: Tuple[int, int] = C.get(self.site,
                                              'screencap_res').split('x')
            self.fps: float = C.getint(self.site, 'screencap_fps')
            self.origin: Tuple[int, int] = C.get(self.site,
                                                 'screencap_origin').split(',')
        elif self.vidsource is None or self.vidsource == 'file':
            self.res: Tuple[int, int] = sio.get_resolution(self.infn,
                                                           self.probeexe)
            self.fps: float = sio.get_framerate(self.infn, self.probeexe)
        else:
            raise ValueError(f'unknown video source {self.vidsource}')

        self.audiofs: int = C.get(self.site, 'audiofs')  # not getint
        self.preset: str = C.get(self.site, 'preset')
        self.timelimit: str = C.get(self.site, 'timelimit', fallback=None)

        self.videochan: str = C.get(sys.platform, 'videochan')
        self.audiochan: str = C.get(sys.platform, 'audiochan', fallback=None)
        self.vcap: str = C.get(sys.platform, 'vcap')
        self.acap: str = C.get(sys.platform, 'acap', fallback=None)
        self.hcam: str = C.get(sys.platform, 'hcam')

        self.video_kbps: int = C.getint(self.site, 'video_kbps', fallback=None)
        self.audio_bps: int = C.get(self.site, 'audio_bps')

        self.keyframe_sec: int = C.getint(self.site, 'keyframe_sec')

        self.server: str = C.get(self.site, 'server', fallback=None)
# %% Key (hexaecimal stream ID)
        keyfn = C.get(self.site, 'key', fallback=None)
        if not keyfn:  # '' or None
            self.key = None
        else:
            # .resolve()  # Python >= 3.6 required for .resolve(strict=False)
            key = Path(keyfn).expanduser()
            self.key = key.read_text().strip() if key.is_file() else keyfn

    def videostream(self) -> Tuple[List[str], List[str]]:
        """optimizes video settings"""
# %% configure video input
        if self.vidsource == 'screen':
            vid1 = self.screengrab()
        elif self.vidsource == 'camera':
            vid1 = self.webcam()
        elif self.vidsource is None or self.vidsource == 'file':
            vid1 = self.filein()
        else:
            raise ValueError(f'unknown vidsource {self.vidsource}')
# %% configure video output
        vid2: List[str] = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p']
# %% set frames/sec, bitrate and keyframe interval
        """
         DON'T DO THIS.
         It makes keyframes/bitrate far off from what streaming sites want
         vid2 += ['-tune', 'stillimage']

         The settings below still save video/data bandwidth for the still image
         + audio case.
        """
        fps = self.fps if self.fps is not None else FPS

        vid2 += ['-preset', self.preset,
                 '-b:v', str(self.video_kbps) + 'k']

        if self.image:
            vid2 += ['-r', str(fps)]

        vid2 += ['-g', str(self.keyframe_sec * fps)]

        return vid1, vid2

    def audiostream(self) -> List[str]:
        """
        -ac * may not be needed, took out.
        -ac 2 NOT -ac 1 to avoid "non monotonous DTS in output stream" errors
        """
        if not self.audio_bps or not self.acap or not self.audiochan:
            return []

        if not self.vidsource == 'file':
            return ['-f', self.acap, '-i', self.audiochan]
        else:  # file input
            return []
#        else: #  file input
#            return ['-ac','2']

    def audiocomp(self) -> List[str]:
        """select audio codec
        https://trac.ffmpeg.org/wiki/Encode/AAC#FAQ
        https://support.google.com/youtube/answer/2853702?hl=en
        https://www.facebook.com/facebookmedia/get-started/live
        """

        if not self.audio_bps or not self.acap or not self.audiochan:
            return []

        return ['-c:a', 'aac',
                '-b:a', str(self.audio_bps),
                '-ar', str(self.audiofs)]

    def video_bitrate(self):
        """get "best" video bitrate.
        Based on YouTube Live minimum specified stream rate."""
        if self.video_kbps:  # per-site override
            return

        if self.res is not None:
            x: int = int(self.res[1])
        elif self.vidsource is None or self.vidsource == 'file':
            logging.info('assuming 480p input.')
            x = 480
        else:
            raise ValueError('Unsure of your video resolution request.'
                             'Try setting video_kpbs in the .ini file.')

        if self.fps is None or self.fps <= 30:
            self.video_kbps: int = list(BR30.values())[
                                    bisect.bisect_left(list(BR30.keys()), x)]
        else:
            self.video_kbps: int = list(BR60.values())[
                                    bisect.bisect_left(list(BR60.keys()), x)]

    def screengrab(self) -> List[str]:
        """choose to grab video from desktop. May not work for Wayland."""
        vid1 = ['-f', self.vcap,
                '-r', str(self.fps)]

        if self.res is not None:
            vid1 += ['-s', 'x'.join(map(str, self.res))]

        if sys.platform == 'linux':
            vid1 += [f'-i', ':0.0+{self.origin[0]},{self.origin[1]}']
        elif sys.platform == 'win32':
            vid1 += ['-offset_x', self.origin[0], '-offset_y', self.origin[1],
                     '-i', self.videochan]
        elif sys.platform == 'darwin':
            vid1 += ['-i', "0:0"]

        return vid1

    def webcam(self) -> List[str]:
        """configure webcam"""
        vid1 = ['-f', self.hcam,
                '-r', str(self.fps),
                '-i', self.videochan]

        return vid1

    def filein(self) -> List[str]:
        """stream input file  (video, or audio + image)"""

        vid1: List[str] = []

        """
        -re is NOT for actual streaming devices (webcam, microphone)
        https://ffmpeg.org/ffmpeg.html
        """

        if self.image:
            vid1 += ['-loop', '1', '-f', 'image2']

        if self.image or self.vidsource == 'file':
            vid1 += ['-re']

        if self.loop:
            vid1 += ['-stream_loop', '-1']  # FFmpeg >= 3

        if self.image:  # still image, for audio-only input files
            vid1 += ['-i', str(self.image)]

        if self.infn:
            vid1 += ['-i', str(self.infn)]

        return vid1

    def buffer(self, server: str) -> List[str]:
        """configure network buffer. Tradeoff: latency vs. robustness"""
        # constrain to single thread, default is multi-thread
        # buf = ['-threads', '1']

        buf = ['-maxrate', f'{self.video_kbps}k',
               '-bufsize', f'{self.video_kbps//2}k']

        if self.image:  # static image + audio
            buf += ['-shortest']

        # for very old versions of FFmpeg, such as Ubuntu 16.04
        # still OK for current FFmpeg versions too
        buf += ['-strict', 'experimental']

        # must manually specify container format when streaming to web.
        buf += ['-f', 'flv']

        return buf


def unify_streams(streams: Dict[str, Stream]) -> str:
    """
    find least common denominator stream settings,
        so "tee" output can generate multiple streams.
    First try: use stream with lowest video bitrate.

    Exploits that Python >= 3.6 has guaranteed dict() ordering.

    fast native Python argmin()
    https://stackoverflow.com/a/11825864
    """
    vid_bw: List[int] = [streams[stream].video_kbps for stream in streams]

    argmin: int = min(range(len(vid_bw)), key=vid_bw.__getitem__)

    key: str = list(streams.keys())[argmin]

    return key
