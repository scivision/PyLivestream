#!/usr/bin/env python
"""
LIVE STREAM TO YOUTUBE LIVE using FFmpeg -- screenshare

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
from PyLivestream import youtubelive


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('ini',help='*.ini file with stream parameters')
    p = p.parse_args()

    P = {'ini': p.ini, 'vidsource': 'screen', 'site': 'youtube'}

    youtubelive(P)
