#!/usr/bin/env python
"""
LIVE STREAM using FFmpeg -- webcam

https://www.scivision.co/youtube-live-ffmpeg-livestream/

Periscope::

    python Webcam.py periscope

YouTube Live::

    python Webcam.py youtube


Facebook::

    python Webcam.py facebook

Facebook Stream Key: https://www.facebook.com/live/create

Windows: get DirectShow device list from::

   ffmpeg -list_devices true -f dshow -i dummy
"""
from typing import List
import PyLivestream

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser(description="livestream webcam")
    p.add_argument('site',
                   help='sites to stream [youtube,periscope,facebook,twitch]',
                   nargs='+')
    p.add_argument('-i', '--ini',
                   help='*.ini file with stream parameters',
                   default='stream.ini')
    p.add_argument('-y', '--yes', help='no confirmation dialog',
                   action='store_true')
    P = p.parse_args()

    S = PyLivestream.Webcam(P.ini, P.site,
                            P.yes)
    sites: List[str] = list(S.streams.keys())
# %% Go live
    if P.yes:
        print('going live on', sites)
    else:
        input(f"Press Enter to go live on {sites}.    Or Ctrl C to abort.")

    S.golive()
