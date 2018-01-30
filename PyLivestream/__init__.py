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


def osparam(P:dict) -> dict:
    """load OS specific config"""

    C = ConfigParser()
    C.read(P['ini'])

    if sys.platform.startswith('linux'):
        if 'XDG_SESSION_TYPE' in os.environ and os.environ['XDG_SESSION_TYPE'] == 'wayland':
            logging.error('Wayland may only give black output with cursor. Login with X11 desktop')

    P['videochan'] = C.get(sys.platform,'videochan')
    P['audiochan'] = C.get(sys.platform,'audiochan')
    P['vcap'] = C.get(sys.platform,'vcap')
    P['acap'] = C.get(sys.platform,'acap')
    P['hcam'] = C.get(sys.platform,'hcam')

    P['audiobw'] = C.get(P['site'],'audiobw')
    P['audiofs'] = C.get(P['site'],'audiofs') # not getint
    P['fps']  = C.getint(P['site'],'fps')
    P['res']  = C.get(P['site'],'res')
    P['origin'] = C.get(P['site'],'origin').split(',')

    return P


# %% video
def _videostream(P:dict) -> tuple:
    """optimizes video settings for YouTube Live"""
# %% configure video input
    if P['vidsource'] == 'screen':
        vid1 = _screengrab(P)
    elif P['vidsource'].startswith('cam'):
        vid1 = _webcam(P)
    elif P['vidsource'] == 'file':
        vid1 = _filein(P)
    else:
        raise ValueError(f'unknown vidsource {P["vidsource"]}')
# %% configure video output
    cvbr = _bitrate(P)

    vid2 = ['-c:v','libx264','-pix_fmt','yuv420p']

    if 'image' in P and P['image']:
        vid2 += ['-tune','stillimage']
    else:
        vid2 += ['-preset',COMPPRESET,
                '-b:v',str(cvbr)+'k',
                '-g',_group(P)]


    return vid1, vid2, cvbr


def _group(P:dict) -> str:

    if 'fps' in P:
        g = str(2*P['fps'])
    else: # TODO assume 30 fps
        g = '60'

    return g


def _bitrate(P:dict) -> list:
    if 'image' in P and P['image']:
        return
    elif P['vidsource'] == 'file': # TODO get from input file
        return 3000
    elif 'site' in P and P['site'] == 'periscope':
        return 800  # same for HD and SD Periscope

# %%
    if 'res' in P:
        y = P['res'].split('x')[1]

        if P['fps'] <= 30:
           cvbr = br30[y]
        else:
           cvbr = br60[y]
    else:  # TODO assuming 720 webcam for now
        if P['fps'] <= 30:
            cvbr = br30['720']
        else:
            cvbr = br60['720']

    return cvbr


def _screengrab(P:dict) -> list:
    """choose to grab video from desktop. May not work for Wayland."""
    vid1 = ['-f', P['vcap'],
            '-r',str(P['fps']),
            '-s',P['res']]

    if sys.platform =='linux':
        vid1 += ['-i',f':0.0+{P["origin"][0]},{P["origin"][1]}']
    elif sys.platform =='win32':
        vid1 += ['-i',P['videochan']]
    elif sys.platform == 'darwin':
        pass  # FIXME: verify

    return vid1


def _webcam(P:dict) -> list:
    """configure webcam"""
    vid1 = ['-f',P['hcam'],
            '-r',str(P['fps']),
            '-i',P['videochan']]

    return vid1


def _filein(P:dict) -> list:
    """file input"""
    fn = Path(P['filein']).expanduser()

    if 'image' in P and P['image']:
        vid1 = ['-loop','1']
    else:
        vid1 = ['-re']



    if 'loop' in P and P['loop']:
        vid1 += ['-stream_loop','-1']  # FFmpeg >= 3
    else:
        vid1 += []

    if 'image' in P and P['image']: # still image, typically used with audio-only input files
        vid1 += ['-i',str(P['image'])]


    vid1 += ['-i',str(fn)]

    return vid1


# %% audio
def _audiostream(P:dict) -> list:
    """
    -ac 2 NOT -ac 1 to avoid "non monotonous DTS in output stream" errors
    """
    if not P['vidsource'] == 'file':
        return ['-f',P['acap'], '-ac','2', '-i', P['audiochan']]
    else: #  file input
        return ['-ac','2']


def _audiocomp(P:dict) -> list:
    """select audio codec
    https://trac.ffmpeg.org/wiki/Encode/AAC#FAQ
    https://support.google.com/youtube/answer/2853702?hl=en
    https://www.facebook.com/facebookmedia/get-started/live
    """

    return ['-c:a','aac',
            '-b:a', P['audiobw'],
            '-ar', P['audiofs']]


def _buffer(P:dict, cvbr:int) -> list:
    buf = ['-threads','0']

    if not 'image' in P or not P['image']:
        buf += ['-maxrate','{}k'.format(cvbr),
                  '-bufsize','{}k'.format(2*cvbr)]
    else: # static image + audio
        buf += ['-shortest']

    buf += ['-f','flv']

    return buf

# %% top-level
def facebooklive(P:dict):
    """LIVE STREAM to Facebook Live
    https://www.facebook.com/live/create
    """

    P = osparam(P)

    vid1,vid2,cvbr = _videostream(P)

    aud1 = _audiostream(P)
    aud2 = _audiocomp(P)

    buf = _buffer(P,cvbr)

    cmd = [getexe()] + vid1 + aud1 + vid2 + aud2 + buf

    print('\n',' '.join(cmd),'\n')

    if 'streamid' in P: # for loop case
        streamid = P['streamid']
    else:
        streamid = getpass('Facebook Live Stream ID: ')

#    sp.check_call(cmd+['rtmps://live-api.facebook.com:443/rtmp/' + streamid],
    sp.check_call(cmd+['rtmp://live-api.facebook.com:80/rtmp/' + streamid],
                stdout=sp.DEVNULL)


def periscope(P:dict):
    """LIVE STREAM to Periscope"""

    P = osparam(P)

    vid1,vid2,cvbr = _videostream(P)

    aud1 = _audiostream(P)
    aud2 = _audiocomp(P)

    buf = _buffer(P,cvbr)

    cmd = [getexe()] + vid1 + aud1 + vid2 + aud2 + buf

    print('\n',' '.join(cmd),'\n')

    if 'streamid' in P: # for loop case
        streamid = P['streamid']
    else:
        streamid = getpass('Periscope Stream ID: ')

    sp.check_call(cmd+['rtmp://va.pscp.tv:80/x/' + streamid],
                stdout=sp.DEVNULL)


def youtubelive(P:dict):
    """LIVE STREAM to YouTube Live"""

    P = osparam(P)

    vid1,vid2,cvbr = _videostream(P)

    aud1 = _audiostream(P)
    aud2 = _audiocomp(P)

    buf = _buffer(P,cvbr)

    cmd = [getexe()] + vid1 + aud1 + vid2 + aud2 + buf

    print('\n',' '.join(cmd),'\n')

    if 'streamid' in P: # for loop case
        streamid = P['streamid']
    else:
        streamid = getpass('YouTube Live Stream ID: ')

    sp.check_call(cmd+['rtmp://a.rtmp.youtube.com/live2/' + streamid],
                stdout=sp.DEVNULL)


def disksave(P:dict, outfn:Path=None):
    """
    records to disk screen capture with audio for upload to YouTube

    if not outfn, just cite command that would have run
    """
    if outfn:
        outfn = Path(outfn).expanduser()

    P = osparam(P)

    vid1 = _screengrab(P)

    aud1 = _audiostream(P)
    aud2 = _audiocomp(P)

    cmd = [getexe()] + vid1 + aud1 + aud2
    if sys.platform == 'win32':
        cmd += ['-copy_ts']

    print('\n',' '.join(cmd),'\n')

    if outfn:
        sp.check_call(cmd + [str(outfn)])
    else:
        print('specify filename to save screen capture with audio to disk.')

