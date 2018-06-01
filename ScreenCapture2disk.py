#!/usr/bin/env python
"""
Save to disk screen capture for upload to YOUTUBE using FFMPEG

https://www.scivision.co/youtube-ffmpeg-screen-capture-with-audio/
https://trac.ffmpeg.org/wiki/Capture/Desktop
https://support.google.com/youtube/answer/2853702

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
import PyLivestream

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('outfn', help='video file to save to disk.')
    p.add_argument('-i', '--ini', help='*.ini file with stream parameters',
                   default='stream.ini')
    p.add_argument('-y', '--yes', help='no confirmation dialog',
                   action='store_true')
    P = p.parse_args()

    s = PyLivestream.SaveDisk(P.ini, P.outfn, yes=P.yes)
# %%
    if P.yes:
        print('saving screen capture to', s.outfn)
    else:
        input(f"Press Enter to screen capture to file {s.outfn}"
              "Or Ctrl C to abort.")

    s.save()
