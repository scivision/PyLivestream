#!/usr/bin/env python
"""
Save to disk screen capture for upload to YOUTUBE using FFMPEG

https://www.scivision.co/youtube-ffmpeg-screen-capture-with-audio/
https://trac.ffmpeg.org/wiki/Capture/Desktop
https://support.google.com/youtube/answer/2853702

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
import pylivestream as pls
import signal
from argparse import ArgumentParser


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser()
    p.add_argument('outfn', help='video file to save to disk.')
    p.add_argument('-i', '--ini', help='*.ini file with stream parameters')
    p.add_argument('-y', '--yes', help='no confirmation dialog', action='store_true')
    p.add_argument('-t', '--timeout', help='stop streaming after --timeout seconds', type=int)
    P = p.parse_args()

    s = pls.SaveDisk(P.ini, P.outfn, yes=P.yes, timeout=P.timeout)
# %%
    if P.yes:
        print('saving screen capture to', s.outfn)
    else:
        input(f"Press Enter to screen capture to file {s.outfn}"
              "Or Ctrl C to abort.")

    s.save()


if __name__ == '__main__':
    main()
