#!/usr/bin/env python
"""
LIVE STREAM using FFmpeg -- screenshare

https://www.scivision.co/youtube-live-ffmpeg-livestream/

Periscope::

    python Screenshare.py periscope


YouTube Live::

    python Screenshare.py youtube


Facebook::

    python Screenshare.py facebook


Facebook Stream Key: https://www.facebook.com/live/create

Windows: get DirectShow device list from::

   ffmpeg -list_devices true -f dshow -i dummy
"""
import PyLivestream


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('site',help='site(s) to stream to [youtube,periscope,facebook,twitch]',nargs='+')
    p.add_argument('-i','--ini',help='*.ini file with stream parameters',default='stream.ini')
    p = p.parse_args()

    PyLivestream.Screenshare(p.ini, p.site)
