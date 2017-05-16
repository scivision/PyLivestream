#!/usr/bin/env python
"""
Cross-platform screen/desktop capture for YouTube (and others) using FFmpeg

https://www.scivision.co/youtube-ffmpeg-screen-capture-with-audio/

https://trac.ffmpeg.org/wiki/Capture/Desktop

https://support.google.com/youtube/answer/2853702
"""
from youtubelive import youtube

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('outfn',help='output file to write',nargs='?')
    p.add_argument('-fps',default=10,type=int)
    p.add_argument('-res',default='1024x720')
    p.add_argument('-o','--origin',help='x,y coordinates of upper-left hand capture area (pixel)',nargs=2,type=int,default=[0,0])
    p = p.parse_args()

    P = {'fps': p.fps,
         'res': p.res,
         'origin':p.origin,
         'audiochan': 'default',
         'Nchan': 1
            }

    youtube(P,p.outfn)
