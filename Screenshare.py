#!/usr/bin/env python
"""
LIVE STREAM using FFmpeg -- screenshare

https://www.scivision.co/youtube-live-ffmpeg-livestream/

Periscope::

    python Screenshare.py stream.ini periscope

https://www.pscp.tv/help/external-encoders

YouTube Live::

    python Screenshare.py stream.ini youtube


https://support.google.com/youtube/answer/2853702

Facebook::

    python Screenshare.py stream.ini facebook

https://www.facebook.com/facebookmedia/get-started/live
Facebook Stream Key:
https://www.facebook.com/live/create

Windows: get DirectShow device list from::

   ffmpeg -list_devices true -f dshow -i dummy
"""
import PyLivestream


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('ini',help='*.ini file with stream parameters')
    p.add_argument('site',help='site to stream to [youtube,periscope,facebook]')
    p = p.parse_args()

    PyLivestream.Screenshare(p.ini, p.site)
