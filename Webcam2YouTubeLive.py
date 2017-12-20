#!/usr/bin/env python
"""
LIVE STREAM TO YOUTUBE LIVE using FFMPEG -- from webcam

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
from youtubelive_ffmpeg import youtubelive
import sys
#
if sys.platform.startswith('win'):
    audiochan = 'audio="Internal Microphone"'
    videochan = 'video="Integrated Camera"'
elif sys.platform.startswith('darwin'):
    audiochan = 'default'
    videochan = 'default'
elif sys.platform.startswith('linux'):
    audiochan = 'default'
    videochan = '/dev/video0'

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-fps',default=30, type=int)
    p = p.parse_args()

    P = {'fps': p.fps,
         'audiochan': audiochan,
         'videochan': videochan,
         'vidsource': 'camera',
            }

    youtubelive(P)
