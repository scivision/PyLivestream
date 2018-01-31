from pathlib import Path
from getpass import getpass
import subprocess as sp
import logging,os,sys
from configparser import ConfigParser
# %% Key is vertical pixels (height). Units kbps
BR30 = {'2160':13000,
        '1440':6000,
        '1080':3000,
        '720':1800,
        '540':800,
        '480':500,
        '360':400,
        '240':300,
        }

BR60 = {'2160':20000,
        '1440':9000,
        '1080':4500,
        '720':2250,
        }


COMPPRESET='veryfast'


def getexe() -> str:
    """checks that host streaming program is installed"""

    try:
        sp.check_call(('ffmpeg','-h'), stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        exe = 'ffmpeg'
    except FileNotFoundError:
        try:
            sp.check_call(('avconv','-h'), stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            exe = 'avconv'
        except FileNotFoundError:
            raise FileNotFoundError('FFmpeg program is not found. Is ffmpeg on your PATH?')

    return exe


def get_framerate(fn:Path) -> float:
    """
    get framerate of video file
    http://trac.ffmpeg.org/wiki/FFprobeTips#FrameRate
    """
    fn = Path(fn).expanduser()

    fps = sp.check_output(['ffprobe','-v','error',
                           '-select_streams','v:0','-show_entries','stream=avg_frame_rate',
                           '-of','default=noprint_wrappers=1:nokey=1', str(fn)], universal_newlines=True)

    fps = fps.strip().split('/')
    fps = int(fps[0]) / int(fps[1])

    return fps


def get_resolution(fn:Path) -> tuple:
    """
    get resolution (widthxheight) of video file
    http://trac.ffmpeg.org/wiki/FFprobeTips#WidthxHeight
    """
    fn = Path(fn).expanduser()

    res = sp.check_output(['ffprobe','-v','error',
                           '-of','flat=s=_',
                           '-select_streams','v:0',
                           '-show_entries','stream=height,width', str(fn)], universal_newlines=True)

    res = res.strip().split('\n')
    res = (int(res[0].split('=')[-1]), int(res[1].split('=')[-1]))

    print(res)

    return res



# %% top level
class Stream:

    def __init__(self,ini,site,vidsource,image=False,loop=False,infn=None):
        self.ini = ini
        self.site = site
        self.vidsource = vidsource
        self.image = image
        self.loop = loop
        self.infn = infn


    def osparam(self):
        """load OS specific config"""

        C = ConfigParser()
        C.read(str(self.ini))

        if sys.platform.startswith('linux'):
            if 'XDG_SESSION_TYPE' in os.environ and os.environ['XDG_SESSION_TYPE'] == 'wayland':
                logging.error('Wayland may only give black output with cursor. Login with X11 desktop')

        self.videochan = C.get(sys.platform,'videochan')
        self.audiochan = C.get(sys.platform,'audiochan')
        self.vcap = C.get(sys.platform,'vcap')
        self.acap = C.get(sys.platform,'acap')
        self.hcam = C.get(sys.platform,'hcam')

        self.video_kbps = C.getint(self.site, 'video_kbps', fallback=None)
        self.audio_bps = C.get(self.site,'audio_bps')
        self.audiofs = C.get(self.site,'audiofs') # not getint
        self.fps  = C.getint(self.site,'fps')
        self.keyframe_sec = C.getint(self.site,'keyframe_sec')
        self.res  = C.get(self.site,'res')
        self.origin = C.get(self.site,'origin').split(',')

        self.server = C.get(self.site,'server', fallback=None)

        keyfn = C.get(self.site,'key', fallback=None)
        if not keyfn:
            self.key = None
        else:
            self.key = Path(keyfn).expanduser().read_text().strip()


    def videostream(self) -> tuple:
        """optimizes video settings for YouTube Live"""
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
            vid2 += ['-preset',COMPPRESET,
                    '-b:v',str(self.video_kbps)+'k',
                    '-g', str(self.keyframe_sec*self.fps)]

        return vid1,vid2


    def audiostream(self) -> list:
        """
        -ac 2 NOT -ac 1 to avoid "non monotonous DTS in output stream" errors
        """
        if not self.vidsource == 'file':
            return ['-f', self.acap, '-ac','2', '-i', self.audiochan]
        else: #  file input
            return ['-ac','2']


    def audiocomp(self) -> list:
        """select audio codec
        https://trac.ffmpeg.org/wiki/Encode/AAC#FAQ
        https://support.google.com/youtube/answer/2853702?hl=en
        https://www.facebook.com/facebookmedia/get-started/live
        """

        return ['-c:a','aac',
                '-b:a', self.audio_bps,
                '-ar', self.audiofs]


    def video_bitrate(self) -> list:
        """get "best" video bitrate"""
        if self.video_kbps:
            return

        if self.res:
            y = self.res.split('x')[1]

            if self.fps <= 30:
               self.video_kbps = BR30[y]
            else:
               self.video_kbps = BR60[y]
        else:  # TODO assuming 720 webcam for now
            if self.fps <= 30:
                self.video_kbps = BR30['720']
            else:
                self.video_kbps = BR60['720']


    def screengrab(self) -> list:
        """choose to grab video from desktop. May not work for Wayland."""
        vid1 = ['-f', self.vcap,
                '-r', str(self.fps),
                '-s', self.res]

        if sys.platform =='linux':
            vid1 += ['-i', ':0.0+{},{}'.format(self.origin[0], self.origin[1])]
        elif sys.platform =='win32':
            vid1 += ['-i', self.videochan]
        elif sys.platform == 'darwin':
            pass  # FIXME: verify

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

        if self.image:
            vid1 = ['-loop','1']
        else:
            vid1 = ['-re']


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


    def unify_streams(self,streams:list) -> int:
        """
        find least common denominator stream settings so "tee" output can generate multiple streams.
        First try: use stream with lowest video bitrate.

        fast native Python argmin()
        https://stackoverflow.com/a/11825864
        """
        vid_bw = [stream.video_kbps for stream in streams]

        return min(range(len(vid_bw)), key=vid_bw.__getitem__)


class Livestream(Stream):

    def __init__(self,ini,site,vidsource,image=False,loop=False,infn=None):
        super().__init__(ini,site,vidsource,image,loop,infn)

        self.site = site

        self.osparam()

        self.video_bitrate()

        vid1,vid2 = self.videostream()

        aud1 = self.audiostream()
        aud2 = self.audiocomp()

        buf = self.buffer()

        cmd = [getexe()] + vid1 + aud1 + vid2 + aud2 + buf

        if self.key:
            streamid = self.key
        else:
            print('\n',' '.join(cmd),'\n')
            streamid = getpass('{} Live Stream ID: '.format(self.site))

        self.sink = [self.server + streamid]

        self.cmd = cmd + self.sink


    def golive(self, sinks:list=None):
        """finally start the stream(s)"""

        if self.sink[0].endswith('test'):
            print('\n',' '.join(self.cmd),'\n')
            return

        if sinks is None: # single stream
            print('\n',' '.join(self.cmd))
            sp.check_call(self.cmd, stdout=sp.DEVNULL)
        else: # multi-stream output tee
            cmdstem = self.cmd[:-3]
            # +global_header is necessary to tee to Periscope (and other services at same time)
            cmd = cmdstem + ['-flags:v','+global_header',
                             '-f','tee','-map','0:v','-map','1:a']
            cmd += ['[f=flv]'+'|[f=flv]'.join(sinks)] # no double quotes
            print(' '.join(cmd))

            sp.check_call(cmd, stdout=sp.DEVNULL)



# %% operators
class Screenshare(Livestream):

    def __init__(self, ini:Path, sites:list):

        if isinstance(sites,str):
            sites = [sites]

        sites = [site.lower() for site in sites]
        vidsource = 'screen'
        ini=Path(ini).expanduser()

        streams = []
        for site in sites:
            print('Config',site)
            streams.append(Livestream(ini,site,vidsource))

        if len(streams)==1:
            streams[0].golive()
            return

        sinks = [stream.sink[0] for stream in streams]

        streams[self.unify_streams(streams)].golive(sinks)


class Webcam(Livestream):

    def __init__(self, ini:Path, site:str):

        site = site.lower()
        vidsource = 'camera'
        ini=Path(ini).expanduser()

        stream = Livestream(ini,site,vidsource)

        stream.golive()


class FileIn(Livestream):

    def __init__(self, ini:Path, site:str, infn:Path, loop:bool=False, image:bool=False):

        site = site.lower()
        vidsource = 'file'
        ini=Path(ini).expanduser()

        stream = Livestream(ini, site, vidsource, image, loop, infn)

        stream.golive()


class SaveDisk(Stream):

    def __init__(self, ini:Path, outfn:Path=None, vidsource:str='screen'):
        """
        records to disk screen capture with audio

        if not outfn, just cite command that would have run
        """
        site = 'file'
        vidsource = 'screen'
        ini=Path(ini).expanduser()

        super().__init__(ini,site,vidsource)

        if outfn:
            outfn = Path(outfn).expanduser()

        self.osparam()

        vid1 = self.screengrab()

        aud1 = self.audiostream()
        aud2 = self.audiocomp()

        cmd = [getexe()] + vid1 + aud1 + aud2 + [str(outfn)]
        if sys.platform == 'win32':
            cmd += ['-copy_ts']

        print('\n',' '.join(cmd),'\n')

        if outfn:
            sp.check_call(cmd )
        else:
            print('specify filename to save screen capture with audio to disk.')
