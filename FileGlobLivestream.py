#!/usr/bin/env python
"""
LIVE STREAM using FFMPEG -- Globbed input file list

NOTE: most video streaming sites REQUIRE you have to a video feed, so try the `-image` option with a favorite .JPG or whatever.

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
from pathlib import Path
import PyLivestream


def playonce(flist:list, image:Path):

    for f in flist:
        s = PyLivestream.FileIn(p.ini, p.site, f, loop=False, image=image)

        s.golive()


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser(description="Livestream a globbed input file list")
    p.add_argument('site',help='site to stream to [youtube,periscope,facebook,twitch]')
    p.add_argument('path',help='path to discover files from')
    p.add_argument('glob',help='file glob pattern to stream.')
    p.add_argument('-i','--ini',help='*.ini file with stream parameters',default='stream.ini')
    p.add_argument('-image',help='static image to display, typically used for audio-only files.')
    p.add_argument('-loop',help='repeat the globbed file list endlessly',action='store_true')
    p.add_argument('-y','--yes',help='no confirmation dialog',action='store_true')
    p = p.parse_args()

    path = Path(p.path).expanduser()
    flist = list(path.glob(p.glob))

    if not flist:
        raise FileNotFoundError('did not find any video files with {} {}'.format(path,p.glob))

    print('streaming these files. Be sure list is correct! \n')
    print('\n'.join(map(str,flist)))
    print()

    if p.yes:
        print('going live on',p.site)
    else:
        input("Press Enter to go live on {}.    Or Ctrl C to abort.".format(p.site))

    if p.loop:
        while True:
            playonce(flist, p.image)
    else:
        playonce(flist, p.image)
