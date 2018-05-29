from collections import OrderedDict # not needed python >= 3.6
import bisect
from pathlib import Path
import logging,os,sys
from configparser import ConfigParser
from typing import Tuple
#
from . import io as sio

# %%  Col0: vertical pixels (height). Col1: video kbps. Interpolates between these resolutions.
BR30 = OrderedDict([
        (240,300),
        (360,400),
        (480,500),
        (540,800),
        (720,1800),
       (1080,3000),
       (1440,6000),
       (2160,13000)])

BR60 = OrderedDict([
       (720,2250),
       (1080,4500),
       (1440,9000),
       (2160,20000)])


# %% top level
class Stream:

    def __init__(self,ini:Path, site:str, vidsource:str, image:bool=False, loop:bool=False, infn:Path=None):
        self.ini = Path(ini).expanduser()
        self.site = site
        self.vidsource = vidsource
        self.image = image
        self.loop = loop
        self.infn = infn


    def osparam(self):
        """load OS specific config"""

        assert self.ini.is_file(),'{} not found.'.format(self.ini)

        C = ConfigParser()
        C.read(str(self.ini))

        assert self.site in C,'Your site {} is not found in {}'.format(self.site,self.ini)

        if 'XDG_SESSION_TYPE' in os.environ:
            if os.environ['XDG_SESSION_TYPE'] == 'wayland':
                logging.error('Wayland may only give black output with cursor. Login with X11 desktop')

        self.exe, self.probeexe = sio.getexe(C.get(sys.platform,'exe',fallback='ffmpeg'))

        if self.vidsource == 'camera':
            self.res = C.get(self.site,'webcam_res').split('x')
            self.fps = C.getint(self.site,'webcam_fps')
        elif self.vidsource == 'screen':
            self.res = C.get(self.site,'screencap_res').split('x')
            self.fps = C.getint(self.site,'screencap_fps')
            self.origin = C.get(self.site,'screencap_origin').split(',')
        elif self.vidsource == 'file':
            self.res = sio.get_resolution(self.infn, self.probeexe)
            self.fps = sio.get_framerate(self.infn, self.probeexe)
        else:
            raise ValueError('unknown video source {}'.format(self.vidsource))

        self.audiofs = C.get(self.site,'audiofs') # not getint
        self.preset = C.get(self.site,'preset')
        self.timelimit = C.get(self.site,'timelimit',fallback=None)

        self.videochan = C.get(sys.platform,'videochan')
        self.audiochan = C.get(sys.platform,'audiochan', fallback=None)
        self.vcap = C.get(sys.platform,'vcap')
        self.acap = C.get(sys.platform,'acap', fallback=None)
        self.hcam = C.get(sys.platform,'hcam')


        self.video_kbps = C.getint(self.site, 'video_kbps', fallback=None)
        self.audio_bps = C.get(self.site,'audio_bps')

        self.keyframe_sec = C.getint(self.site,'keyframe_sec')

        self.server = C.get(self.site,'server', fallback=None)
# %% Key (hexaecimal stream ID)
        keyfn = C.get(self.site,'key', fallback=None)
        if not keyfn:  # '' or None
            self.key = None
        else:
            key = Path(keyfn).expanduser()#  .resolve()  # Python >= 3.6 required for .resolve(strict=False)
            self.key = key.read_text().strip() if key.is_file() else keyfn


    def videostream(self) -> Tuple[list,list]:
        """optimizes video settings"""
# %% configure video input
        if self.vidsource == 'screen':
            vid1 = self.screengrab()
        elif self.vidsource == 'camera':
            vid1 = self.webcam()
        elif self.vidsource == 'file':
            vid1 = self.filein()
        else:
            raise ValueError('unknown vidsource {}'.format(self.vidsource))
# %% configure video output
        vid2 = ['-c:v','libx264','-pix_fmt','yuv420p']

        if self.image:
            vid2 += ['-tune','stillimage']
        else:
            fps = self.fps if self.fps is not None else 30.

            vid2 += ['-preset',self.preset,
                    '-b:v',str(self.video_kbps)+'k',
                    '-g', str(self.keyframe_sec*fps)]

        return vid1,vid2


    def audiostream(self) -> list:
        """
        -ac * may not be needed, took out.
        -ac 2 NOT -ac 1 to avoid "non monotonous DTS in output stream" errors
        """
        if not self.audio_bps or not self.acap or not self.audiochan:
            return []

        if not self.vidsource == 'file':
            return ['-f', self.acap, '-i', self.audiochan]
        else: # file input
            return []
#        else: #  file input
#            return ['-ac','2']


    def audiocomp(self) -> list:
        """select audio codec
        https://trac.ffmpeg.org/wiki/Encode/AAC#FAQ
        https://support.google.com/youtube/answer/2853702?hl=en
        https://www.facebook.com/facebookmedia/get-started/live
        """

        if not self.audio_bps or not self.acap or not self.audiochan:
            return []

        return ['-c:a','aac',
                '-b:a', self.audio_bps,
                '-ar', self.audiofs]


    def video_bitrate(self):
        """get "best" video bitrate.
        Based on YouTube Live minimum specified stream rate."""
        if self.video_kbps: # per-site override
            return

        if self.res is not None:
            x = int(self.res[1])
        elif self.vidsource == 'file':
            logging.warning('assuming 720p input.')
            x = 720


        if self.fps is None or self.fps <= 30:
            self.video_kbps = list(BR30.values())[bisect.bisect_left(list(BR30.keys()), x)]
        else:
            self.video_kbps = list(BR60.values())[bisect.bisect_left(list(BR60.keys()), x)]


    def screengrab(self) -> list:
        """choose to grab video from desktop. May not work for Wayland."""
        vid1 = ['-f', self.vcap,
                '-r', str(self.fps)]

        if self.res is not None:
            vid1 += ['-s', 'x'.join(self.res)]

        if sys.platform =='linux':
            vid1 += ['-i', ':0.0+{},{}'.format(self.origin[0], self.origin[1])]
        elif sys.platform =='win32':
            vid1 += ['-offset_x',self.origin[0],'-offset_y',self.origin[1],
                     '-i', self.videochan,]
        elif sys.platform == 'darwin':
            vid1 += ['-i',"0:0"]

        return vid1


    def webcam(self) -> list:
        """configure webcam"""
        vid1 = ['-f', self.hcam,
                '-r', str(self.fps),
                '-i', self.videochan]

        return vid1


    def filein(self) -> list:
        """stream input file  (video, or audio + image)"""

        fn = Path(self.infn).expanduser()

        vid1 = ['-loop','1'] if self.image else ['-re']

        if self.loop:
            vid1 += ['-stream_loop','-1']  # FFmpeg >= 3
        else:
            vid1 += []

        if self.image: # still image, typically used with audio-only input files
            vid1 += ['-i',str(self.image)]


        vid1 += ['-i',str(fn)]

        return vid1


    def buffer(self) -> list:
        """configure network buffer. Tradeoff: latency vs. robustness"""
        buf = ['-threads','0']

        if not self.image:
            buf += ['-maxrate','{}k'.format(self.video_kbps),
                      '-bufsize','{}k'.format(2*self.video_kbps)]
        else: # static image + audio
            buf += ['-shortest']

        buf += ['-f','flv']

        return buf


    def unify_streams(self, streams:list) -> int:
        """
        find least common denominator stream settings so "tee" output can generate multiple streams.
        First try: use stream with lowest video bitrate.

        fast native Python argmin()
        https://stackoverflow.com/a/11825864
        """
        if not streams:
            return

        vid_bw = [stream.video_kbps for stream in streams]

        return min(range(len(vid_bw)), key=vid_bw.__getitem__)