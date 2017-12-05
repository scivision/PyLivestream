#!/usr/bin/env python
"""
LIVE STREAM TO YOUTUBE LIVE using FFMPEG -- Globbed input file list

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
from pathlib import Path
from youtubelive_ffmpeg import youtubelive

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('path',help='path to discover files from')
    p.add_argument('glob',help='file glob pattern for YouTube Live.  Keep in mind copyright and TOS!')
    p = p.parse_args()

    path = Path(p.path).expanduser()
    flist = list(path.glob(p.glob))

    if not flist:
        raise FileNotFoundError('did not find any video files with {} {}'.format(path,p.glob))

    print('streaming to YouTube Live these files. Be sure list is correct! \n')
    print('\n'.join([str(f) for f in flist]))

    for f in flist:
        P = {'filein': f,
             'fps':30, # TODO auto-determine input FPS
             'audiochan': 'default',
             'vidsource': 'file',
                }

        youtubelive(P)
