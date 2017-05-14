#!/usr/bin/env python
"""
Cross-platform live streaming to YouTube Live using FFmpeg

https://www.scivision.co/youtube-live-ffmpeg-livestream/

https://trac.ffmpeg.org/wiki/EncodingForStreamingSites

https://trac.ffmpeg.org/wiki/Capture/Desktop

https://support.google.com/youtube/answer/2853702
"""
import subprocess as S
from getpass import getpass

try:
    S.check_call(('ffmpeg','-h'), stdout=S.DEVNULL)
except S.CalledProcessError:
    raise FileNotFoundError('FFmpeg is not installed for your system.')

streamfps = 30
res = '1024x720'
origin = ':0.0+0,24'
COMPPRESET='veryfast'

audiochan = 'hw:1,0'
Nchan = '1'

#%% minimum bitrates specified by YouTube. Key is vertical pixels (height)
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

def youtubelive(useaudio=False):
    y = res.split('x')[1]
    
    if streamfps <= 30:
       cvbr = br30[y]
    else:
       cvbr = br60[y]
    

    vid1 = ['-f', 'x11grab',
            '-r',str(streamfps),'-s',res,'-i',origin]

    vid2 = ['-vcodec','libx264','-pix_fmt','yuv420p',
            '-preset',COMPPRESET,
            '-b:v',str(cvbr)+'k',
            '-g',str(2*streamfps)]

    if useaudio:
        aud1 = ['-f','alsa','-ac',Nchan,'-i',audiochan]
        aud2 = ['-acodec','libmp3lame','-ar','44100' ]
    else:
        aud1 = aud2 = []

    codec = ['-threads','0',
             '-bufsize',str(2*cvbr)+'k',
            '-f','flv']



    cmd = ['ffmpeg'] + vid1 + aud1 + vid2 + aud2 + codec

    print(' '.join(cmd))

    S.run(cmd+('rtmp://a.rtmp.youtube.com/live2/'+getpass('YouTube Live Stream ID: '),),
                stdout=S.DEVNULL)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('--audio',help='stream audio',action='store_true')
    p = p.parse_args()

    youtubelive(p.audio)
