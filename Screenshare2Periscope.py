#!/usr/bin/env python
"""
LIVE STREAM TO Periscope using FFMPEG -- screenshare

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://www.pscp.tv/help/external-encoders

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
from PyLivestream import periscope


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('ini',help='*.ini file with stream parameters')
    p = p.parse_args()

    P = {'ini': p.ini, 'vidsource': 'screen', 'site': 'periscope'}

    periscope(P)

