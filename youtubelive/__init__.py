from pathlib import Path
from getpass import getpass
import subprocess as S
from sys import platform
# %%
try:
    S.check_call(('ffmpeg','-h'), stdout=S.DEVNULL, stderr=S.DEVNULL)
except S.CalledProcessError:
    raise FileNotFoundError('FFmpeg is not installed for your system.')
# %% https://trac.ffmpeg.org/wiki/Capture/Desktop
if platform.startswith('linux'):
    vcap = 'x11grab'
    acap = 'pulse'
elif platform.startswith('darwin'):
    vcap = 'avfoundation'
    acap = '0:0'  # determine from ffmpeg -f avfoundation -list_devices true -i ""
elif platform.startswith('win'):
    vcap = 'dshow'
    acap =' video="UScreenCapture":audio="Microphone"'
else:
    raise RuntimeError('not sure which operating system you are using {}'.format(platform))



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

def videostream(P):

    y = P['res'].split('x')[1]

    if P['fps'] <= 30:
       cvbr = br30[y]
    else:
       cvbr = br60[y]

    vid1 = screengrab(P)

    vid2 = ['-vcodec','libx264','-pix_fmt','yuv420p',
            '-preset',COMPPRESET,
            '-b:v',str(cvbr)+'k',
            '-g',str(2*P['fps'])]

    return vid1,vid2,cvbr

def audiostream(P):

    return ['-f',acap, '-ac',str(P['Nchan']), '-i',P['audiochan']]

def audiocomp(P):

    return ['-acodec','libmp3lame','-ar','48000' ]

def screengrab(P):
    vid1 = ['-f', vcap,
        '-r',str(P['fps']), '-s',P['res'],
        '-i',f':0.0+{P["origin"][0]},{P["origin"][1]}']

    return vid1

def youtubelive(P):
    """
    runs live stream to YouTube Live
    """

    vid1,vid2,cvbr = videostream(P)

    aud1 = audiostream(P)
    aud2 = audiocomp(P)

    codec = ['-threads','0',
             '-bufsize',str(2*cvbr)+'k',
            '-f','flv']

    cmd = ['ffmpeg'] + vid1 + aud1 + vid2 + aud2 + codec

    print(' '.join(cmd))

    S.run(cmd+['rtmp://a.rtmp.youtube.com/live2/', getpass('YouTube Live Stream ID: ')],
                stdout=S.DEVNULL)

def youtube(P,outfn):
    """
    records screen capture with audio for YouTube

    if not outfn, just cite command that would have run
    """
    if outfn:
        outfn = Path(outfn).expanduser()

    vid1 = screengrab(P)

    aud1 = audiostream(P)
    aud2 = audiocomp(P)

    cmd = ['ffmpeg'] + vid1 + aud1 + aud2

    print(' '.join(cmd))

    if outfn:
        S.run(cmd + [str(outfn)])

