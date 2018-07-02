#!/usr/bin/env python
"""
LIVE STREAM using FFMPEG -- Looping input file endlessly

NOTE: for audio files,
     use FileGlob2Livestream.py with options `-image myimg.jpg -loop`

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
from typing import List
from pathlib import Path
import PyLivestream
import signal
from argparse import ArgumentParser

R = Path(__file__).parent


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="Livestream a single looped input file")
    p.add_argument('infn', help='file to stream, looping endlessly.')
    p.add_argument('site',
                   help='site to stream: [youtube,periscope,facebook,twitch]',
                   nargs='?', default='localhost')
    p.add_argument('-i', '--ini', help='*.ini file with stream parameters',
                   default=R/'stream.ini')
    p.add_argument('-y', '--yes', help='no confirmation dialog',
                   action='store_true')
    P = p.parse_args()

    site = P.site.split()

    S = PyLivestream.FileIn(P.ini, site, infn=P.infn,
                            loop=True, yes=P.yes)
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
