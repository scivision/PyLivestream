#!/usr/bin/env python
"""
LIVE STREAM TO Periscope using FFMPEG -- screenshare

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://www.facebook.com/facebookmedia/get-started/live

get your Stream Key from:
https://www.facebook.com/live/create

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
from PyLivestream import facebooklive


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('ini',help='*.ini file with stream parameters')
    p = p.parse_args()

    P = {'ini': p.ini, 'vidsource': 'screen', 'site': 'facebook'}

    facebooklive(P)

