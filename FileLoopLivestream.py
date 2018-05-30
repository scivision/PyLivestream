#!/usr/bin/env python
"""
LIVE STREAM using FFMPEG -- Looping input file endlessly

NOTE: for audio files,
     use FileGlob2Livestream.py with options `-image myimg.jpg -loop`

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
import PyLivestream

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser(description="Livestream a single looped input file")
    p.add_argument('infn', help='file to stream, looping endlessly.')
    p.add_argument('site',
                   help='site to stream: [youtube,periscope,facebook,twitch]')
    p.add_argument('-i', '--ini', help='*.ini file with stream parameters',
                   default='stream.ini')
    p.add_argument('-y', '--yes', help='no confirmation dialog',
                   action='store_true')
    P = p.parse_args()

    s = PyLivestream.FileIn(P.ini, P.site, P.infn, loop=True, yes=P.yes)
# %% Go live
    if P.yes:
        print('going live on', s.stream.site, 'looping file', s.stream.infn)
    else:
        input(f"Press Enter to go live on {s.stream.site},"
              f"looping file {s.stream.infn}.")
        print('Or Ctrl C to abort.')

    s.golive()
