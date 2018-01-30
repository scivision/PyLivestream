#!/usr/bin/env python
"""
LIVE STREAM TO YOUTUBE LIVE using FFMPEG -- Looping input file endlessly

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
from PyLivestream import youtubelive

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('ini',help='config file')
    p.add_argument('filein',help='file to loop endlessly to YouTube Live.  Keep in mind copyright and TOS!')
    p = p.parse_args()

    P = {'ini':p.ini,
         'filein': p.filein,
         'vidsource': 'file',
         'loop':True,
         'site':'youtube',
            }

    youtubelive(P)
