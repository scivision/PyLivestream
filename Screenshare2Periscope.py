#!/usr/bin/env python
"""
LIVE STREAM TO Periscope using FFMPEG -- screenshare

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://www.pscp.tv/help/external-encoders

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
from youtubelive_ffmpeg import periscope
import sys
#
if sys.platform.startswith('win'):
    audiochan = 'audio="Internal Microphone"'
    videochan = 'video="UScreenCapture"'
elif sys.platform.startswith('darwin'):
    audiochan = 'default'
    videochan = 'default'
elif sys.platform.startswith('linux'):
    audiochan = 'default'
    videochan = None

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-r','--res', help='resolution:  HD or SD  (default SD)',default='SD')
    p.add_argument('-o','--origin',help='x,y coordinates of upper-left hand capture area (pixel)',
                   nargs=2,type=int,default=[100,100])
    p = p.parse_args()

    P = {'fps': 30,
         'res': p.res,
         'origin':p.origin,
         'videochan': videochan,
         'audiochan': audiochan,
         'vidsource': 'screen',
            }

    periscope(P)

