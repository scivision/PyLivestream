from pathlib import Path
from getpass import getpass
import subprocess as sp
import logging,os,sys
from configparser import ConfigParser
# %% minimum bitrates specified by YouTube. Key is vertical pixels (height)
br30 = {'2160':13000,
        '1440':6000,
        '1080':3000,
        '720':1500,
        '540':800,
        '480':500,
        '360':400,
        '240':300,
        }

br60 = {'2160':20000,
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

# %% top level
class Stream:

    def __init__(self,ini,site,vidsource,image,loop):
        self.ini = ini
        self.site = site
        self.vidsource = vidsource
        self.image = image
        self.loop = loop


    def osparam(self):
        """load OS specific config"""

        C = ConfigParser()
        C.read(self.ini)

        if sys.platform.startswith('linux'):
            if 'XDG_SESSION_TYPE' in os.environ and os.environ['XDG_SESSION_TYPE'] == 'wayland':
                logging.error('Wayland may only give black output with cursor. Login with X11 desktop')

        self.videochan = C.get(sys.platform,'videochan')
        self.audiochan = C.get(sys.platform,'audiochan')
        self.vcap = C.get(sys.platform,'vcap')
        self.acap = C.get(sys.platform,'acap')
        self.hcam = C.get(sys.platform,'hcam')

        self.audiobw = C.get(self.site,'audiobw')
        self.audiofs = C.get(self.site,'audiofs') # not getint
        self.fps  = C.getint(self.site,'fps')
        self.res  = C.get(self.site,'res')
        self.origin = C.get(self.site,'origin').split(',')

        keyfn = C.get(self.site,'key', fallback=None)
        if not keyfn:
            self.key = None
        else:
            self.key = Path(keyfn).expanduser().read_text()


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
        cvbr = self.bitrate()

        vid2 = ['-c:v','libx264','-pix_fmt','yuv420p']

        if self.image:
            vid2 += ['-tune','stillimage']
        else:
            vid2 += ['-preset',COMPPRESET,
                    '-b:v',str(cvbr)+'k',
                    '-g',self.group()]

        return vid1,vid2,cvbr


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
                '-b:a', self.audiobw,
                '-ar', self.audiofs]

    def group(self) -> str:

        if self.fps:
            g = str(2*self.fps)
        else: # TODO assume 30 fps
            g = '60'

        return g


    def bitrate(self) -> list:
        if self.image:
            return
        elif self.vidsource == 'file': # TODO get from input file
            return 3000
        elif self.site == 'periscope':
            return 800  # same for HD and SD Periscope

    # %%
        if self.res:
            y = self.res.split('x')[1]

            if self.fps <= 30:
               cvbr = br30[y]
            else:
               cvbr = br60[y]
        else:  # TODO assuming 720 webcam for now
            if self.fps <= 30:
                cvbr = br30['720']
            else:
                cvbr = br60['720']

        return cvbr


    def screengrab(self) -> list:
        """choose to grab video from desktop. May not work for Wayland."""
        vid1 = ['-f', self.vcap,
                '-r', str(self.fps),
                '-s', self.res]

        if sys.platform =='linux':
            vid1 += ['-i',f':0.0+{self.origin[0]},{self.origin[1]}']
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
        fn = Path(self.loop).expanduser()

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




    def buffer(self, cvbr:int) -> list:
        buf = ['-threads','0']

        if not self.image:
            buf += ['-maxrate','{}k'.format(cvbr),
                      '-bufsize','{}k'.format(2*cvbr)]
        else: # static image + audio
            buf += ['-shortest']

        buf += ['-f','flv']

        return buf


class Livestream(Stream):

    def __init__(self,ini,site,vidsource,image=False,loop=False):
        super().__init__(ini,site,vidsource,image,loop)

        self.site = site

        self.osparam()

        vid1,vid2,cvbr = self.videostream()

        aud1 = self.audiostream()
        aud2 = self.audiocomp()

        buf = self.buffer(cvbr)

        self.cmd = [getexe()] + vid1 + aud1 + vid2 + aud2 + buf

        print('\n',' '.join(self.cmd),'\n')

    def golive(self):
        if self.site == 'periscope':
            self.periscope()
        elif self.site == 'youtube':
            self.youtubelive()
        elif self.site == 'facebook':
            self.facebooklive()
        else:
            raise ValueError('site {} unknown'.format(self.site))


# %% sites
    def facebooklive(self):
        """
        LIVE STREAM to Facebook Live
        https://www.facebook.com/live/create
        """

        if isinstance(self.key, str):
            streamid = self.key
        else:
            streamid = getpass('Facebook Live Stream ID: ')

        cmd = self.cmd+['rtmp://live-api.facebook.com:80/rtmp/' + streamid]

        if streamid == 'test':
            print(' '.join(cmd))
            return

    #    sp.check_call(self.cmd+['rtmps://live-api.facebook.com:443/rtmp/' + streamid],
        sp.check_call(cmd, stdout=sp.DEVNULL)


    def periscope(self):
        """LIVE STREAM to Periscope"""

        if isinstance(self.key, str):
            streamid = self.key
        else:
            streamid = getpass('Periscope Stream ID: ')

        cmd = self.cmd+['rtmp://va.pscp.tv:80/x/' + streamid]

        if streamid == 'test':
            print(' '.join(cmd))
            return

        sp.check_call(cmd, stdout=sp.DEVNULL)


    def youtubelive(self):
        """LIVE STREAM to YouTube Live"""

        if isinstance(self.key, str):
            streamid = self.key
        else:
            streamid = getpass('YouTube Live Stream ID: ')

        cmd = self.cmd+['rtmp://a.rtmp.youtube.com/live2/' + streamid]

        if streamid == 'test':
            print(' '.join(cmd))
            return

        sp.check_call(cmd, stdout=sp.DEVNULL)

# %% operators
class Screenshare(Livestream):

    def __init__(self, ini:Path, site:str):

        site = site.lower()
        vidsource = 'screen'
        ini=Path(ini).expanduser()
        image = False
        loop = False

        stream = Livestream(ini,site,vidsource,image,loop)

        stream.golive()



class Webcam(Livestream):

    def __init__(self, ini:Path, site:str):

        site = site.lower()
        vidsource = 'camera'
        ini=Path(ini).expanduser()
        image = False
        loop = False

        stream = Livestream(ini,site,vidsource,image,loop)

        stream.golive()


class Loop(Livestream):

    def __init__(self, ini:Path, site:str, infn:Path):

        site = site.lower()
        vidsource = 'file'
        ini=Path(ini).expanduser()
        image = False
        loop = infn

        stream = Livestream(ini,site,vidsource,image,loop)

        stream.golive()



class SaveDisk(Stream):

    def __init__(self,ini:Path, outfn:Path=None):
        """
        records to disk screen capture with audio for upload to YouTube

        if not outfn, just cite command that would have run
        """
        site = vidsource = 'file'
        ini=Path(ini).expanduser()
        image = False
        loop = False

        super().__init__(ini,site,vidsource,image,loop)

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

