from pathlib import Path
from getpass import getpass
import subprocess as sp
from sys import platform
import logging,os
# %%
try:
    sp.check_call(('ffmpeg','-h'), stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    FFMPEG = 'ffmpeg'
except FileNotFoundError:
    try:
        sp.check_call(('avconv','-h'), stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        FFMPEG = 'avconv'
    except FileNotFoundError:
        raise FileNotFoundError('FFmpeg is not installed for your system.')
# %% https://trac.ffmpeg.org/wiki/Capture/Desktop
if platform.startswith('linux'):
    if 'XDG_SESSION_TYPE' in os.environ and os.environ['XDG_SESSION_TYPE'] == 'wayland':
        logging.error('Wayland may only give black output with cursor. Login with X11 desktop')
    vcap = 'x11grab'
    acap = 'pulse'

    cam = '/dev/video0'      # v4l2-ctl --list-devices
    hcam = 'v4l2'
elif platform.startswith('darwin'):
    vcap = 'avfoundation'
    acap = '0:0'  # determine from ffmpeg -f avfoundation -list_devices true -i ""

    cam = 'default'       # ffmpeg -f avfoundation -list_devices true -i ""
    hcam = 'avfoundation'
elif platform.startswith('win'):
    vcap = 'dshow'
    acap = 'video="UScreenCapture":audio="Microphone"'

    cam = 'Integrated Camera'        # ffmpeg -list_devices true -f dshow -i dummy
    hcam = 'dshow'
else:
    raise ValueError('not sure which operating system you are using {}'.format(platform))

# %% minimum bitrates specified by YouTube. Key is vertical pixels (height)
br30 = {'2160':13000,
        '1440':6000,
        '1080':3000,
        '720':1500,
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

# %% video
def _videostream(P:dict) -> tuple:
    """optimizes video settings for YouTube Live"""
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

    if P['vidsource'] == 'screen':
        vid1 = _screengrab(P)
    elif P['vidsource'].startswith('cam'):
        vid1 = _webcam(P)
    elif P['vidsource'] == 'file':
        vid1 = _filein(P)
    else:
        raise ValueError('unknown vidsource {}'.format(P['vidsource']))

    vid2 = ['-vcodec','libx264','-pix_fmt','yuv420p',
            '-preset',COMPPRESET,
            '-b:v',str(cvbr)+'k',
            '-g',str(2*P['fps'])]

    return vid1, vid2, cvbr


def _screengrab(P:dict) -> list:
    """choose to grab video from desktop. May not work for Wayland."""
    vid1 = ['-f', vcap,
            '-r',str(P['fps']),
            '-s',P['res'],
            '-i',f':0.0+{P["origin"][0]},{P["origin"][1]}']

    return vid1


def _webcam(P:dict) -> list:
    """configure webcam"""
    vid1 = ['-f',hcam,
            '-r',str(P['fps']),
            '-i',cam]

    return vid1

def _filein(P:dict) -> list:
    """file input"""
    fn = Path(P['filein']).expanduser()

    if 'loop' in P and P['loop']:
        vid1 = ['-stream_loop','-1']  # FFmpeg >= 3
    else:
        vid1 = []

    vid1 += ['-i',str(fn)]

    return vid1


# %% audio
def _audiostream(P:dict) -> list:
    """
    -ac 2 NOT -ac 1 to avoid "non monotonous DTS in output stream" errors
    """
    return ['-f',acap, '-ac','2', '-i', P['audiochan']]


def _audiocomp(P:dict) -> list:
    """select audio codec"""
    return ['-acodec','libmp3lame','-ar','48000' ]


# %% top-level
def youtubelive(P:dict):
    """LIVE STREAM to YouTube Live"""

    vid1,vid2,cvbr = _videostream(P)

    aud1 = _audiostream(P)
    aud2 = _audiocomp(P)

    codec = ['-threads','0',
             '-bufsize',str(2*cvbr)+'k',
            '-f','flv']

    cmd = [FFMPEG] + vid1 + aud1 + vid2 + aud2 + codec

    print('\n',' '.join(cmd),'\n')

    if 'streamid' in P: # for loop case
        streamid = P['streamid']
    else:
        streamid = getpass('YouTube Live Stream ID: ')

    sp.check_call(cmd+['rtmp://a.rtmp.youtube.com/live2/', streamid],
                stdout=sp.DEVNULL)


def disksave4youtube(P:dict, outfn:Path=None):
    """
    records to disk screen capture with audio for upload to YouTube

    if not outfn, just cite command that would have run
    """
    if outfn:
        outfn = Path(outfn).expanduser()

    vid1 = _screengrab(P)

    aud1 = _audiostream(P)
    aud2 = _audiocomp(P)

    cmd = [FFMPEG] + vid1 + aud1 + aud2

    print('\n',' '.join(cmd),'\n')

    if outfn:
        sp.check_call(cmd + [str(outfn)])
    else:
        print('specify filename to save screen capture with audio to disk.')

