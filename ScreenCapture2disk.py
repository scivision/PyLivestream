#!/usr/bin/env python
"""
Save to disk screen capture for upload to YOUTUBE using FFMPEG

https://www.scivision.co/youtube-ffmpeg-screen-capture-with-audio/
https://trac.ffmpeg.org/wiki/Capture/Desktop
https://support.google.com/youtube/answer/2853702

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
from PyLivestream import disksave

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('ini',help='config file')
    p.add_argument('outfn',help='output file to write',nargs='?')
    p = p.parse_args()

    P = {'ini':p.ini, 'vidsource': 'screen', 'site':'file'}

    disksave(P, p.outfn)
