#!/usr/bin/env python
"""
LIVE STREAM using FFmpeg -- webcam

https://www.scivision.co/youtube-live-ffmpeg-livestream/

Windows: get DirectShow device list from::

   ffmpeg -list_devices true -f dshow -i dummy
"""
from typing import List
import pylivestream as pls
import signal
from argparse import ArgumentParser


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="livestream webcam")
    p.add_argument('websites', help='site to stream, e.g. localhost youtube periscope facebook twitch', nargs='+')
    p.add_argument('-i', '--ini', help='*.ini file with stream parameters')
    p.add_argument('-y', '--yes', help='no confirmation dialog',
                   action='store_true')
    p.add_argument('-t', '--timeout', help='stop streaming after --timeout seconds', type=int)
    P = p.parse_args()

    S = pls.Webcam(P.ini, P.websites, yes=P.yes, timeout=P.timeout)
    sites: List[str] = list(S.streams.keys())
# %% Go live
    if P.yes:
        print('going live on', sites)
    else:
        input(f"Press Enter to go live on {sites}.    Or Ctrl C to abort.")

    S.golive()


if __name__ == '__main__':
    main()
