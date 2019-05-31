#!/usr/bin/env python
"""
Livestream: Image + microphone audio
"""

import pylivestream as pls
import signal
from argparse import ArgumentParser


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="livestream microphone audio")
    p.add_argument('websites', help='site to stream, e.g. localhost youtube periscope facebook twitch', nargs='+')
    p.add_argument('-image', help='static image to display.')
    p.add_argument('-i', '--ini', help='*.ini file with stream parameters')
    p.add_argument('-y', '--yes', help='no confirmation dialog', action='store_true')
    p.add_argument('-t', '--timeout', help='stop streaming after --timeout seconds', type=int)
    P = p.parse_args()

    s = pls.Microphone(P.ini, P.websites, image=P.image, yes=P.yes, timeout=P.timeout)
    sites = list(s.streams.keys())
# %% Go live
    if P.yes:
        print('going live on', sites)
    else:
        input(f"Press Enter to go live on {sites}.    Or Ctrl C to abort.")

    s.golive()


if __name__ == '__main__':
    main()
