#!/usr/bin/env python
"""
LIVE STREAM using FFMPEG -- Looping input file endlessly

NOTE: for audio files, instead use FileGlob2Livestream.py with options `-image myimg.jpg -loop`

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
import PyLivestream

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('infn',help='file to stream, looping endlessly.')
    p.add_argument('site',help='site to stream to [youtube,periscope,facebook,twitch]')
    p.add_argument('-i','--ini',help='*.ini file with stream parameters',default='stream.ini')
    p.add_argument('-y','--yes',help='no confirmation dialog',action='store_true')
    p = p.parse_args()


    s = PyLivestream.FileIn(p.ini, p.site, p.infn, loop=True)
# %% Go live
    if p.yes:
        print('going live on',s.stream.site,'looping file',s.stream.infn)
    else:
        input("Press Enter to go live on {}, looping file {}.    Or Ctrl C to abort.".format(s.stream.site, s.stream.infn))

    s.golive()
