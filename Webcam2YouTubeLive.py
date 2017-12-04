#!/usr/bin/env python
"""
LIVE STREAM TO YOUTUBE LIVE using FFMPEG -- from webcam

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
from youtubelive_ffmpeg import youtubelive

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-fps',default=30, type=int)
    p = p.parse_args()

    P = {'fps': p.fps,
         'audiochan': 'default',
         'vidsource': 'camera',
            }

    youtubelive(P)
