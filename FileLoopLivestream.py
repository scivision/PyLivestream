#!/usr/bin/env python
"""
LIVE STREAM using FFMPEG -- Looping input file endlessly

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
import PyLivestream

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('ini',help='*.ini file with stream parameters')
    p.add_argument('site',help='site to stream to [youtube,periscope,facebook,twitch]')
    p.add_argument('infn',help='file to stream, looping endlessly.')
    p = p.parse_args()


    PyLivestream.FileIn(p.ini, p.site, p.infn, loop=True)
