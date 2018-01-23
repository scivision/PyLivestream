#!/usr/bin/env python
"""
LIVE STREAM TO Periscope using FFMPEG -- screenshare

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://www.facebook.com/facebookmedia/get-started/live

Windows: get DirectShow device list from:
   ffmpeg -list_devices true -f dshow -i dummy
"""
from youtubelive_ffmpeg import facebooklive
import sys
import webbrowser

#
if sys.platform.startswith('win'):
    audiochan = 'audio="Internal Microphone"'
    videochan = 'video="UScreenCapture"'
elif sys.platform.startswith('darwin'):
    audiochan = 'default'
    videochan = 'default'
elif sys.platform.startswith('linux'):
    audiochan = 'default'
    videochan = None

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-o','--origin',help='x,y coordinates of upper-left hand capture area (pixel)',
                   nargs=2,type=int,default=[100,100])
    p = p.parse_args()

    P = {'fps': 30,
         'res': '1280x720',
         'origin':p.origin,
         'videochan': videochan,
         'audiochan': audiochan,
         'vidsource': 'screen',
            }

    print('\nGet your Stream Key from:')
    print('https://www.facebook.com/live/create\n')    
    print('Be sure not to have your Stream Key visible on the screen when you start to stream!')
    

    facebooklive(P)

