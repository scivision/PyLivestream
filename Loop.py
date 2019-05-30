#!/usr/bin/env python
"""
LIVE STREAM using FFMPEG -- Looping input file endlessly

NOTE: for audio files,
     use FileGlob2Livestream.py with options `-image myimg.jpg -loop`

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
from typing import List
import pylivestream as pls
import signal
from argparse import ArgumentParser


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="Livestream a single looped input file")
    p.add_argument('infn', help='file to stream, looping endlessly.')
    p.add_argument('websites', help='site to stream, e.g. localhost youtube periscope facebook twitch', nargs='+')
    p.add_argument('-i', '--ini', help='*.ini file with stream parameters')
    p.add_argument('-y', '--yes', help='no confirmation dialog', action='store_true')
    p.add_argument('-t', '--timeout', help='stop streaming after --timeout seconds', type=int)
    P = p.parse_args()

    S = pls.FileIn(P.ini, P.websites, infn=P.infn, loop=True, yes=P.yes, timeout=P.timeout)
    sites: List[str] = list(S.streams.keys())
# %% Go live
    if P.yes:
        print(f'going live on {sites} looping file {P.infn}')
    else:
        input(f"Press Enter to go live on {sites},"
              f"looping file {P.infn}")
        print('Or Ctrl C to abort.')

    S.golive()


if __name__ == '__main__':
    main()
