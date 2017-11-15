#!/usr/bin/env python
import youtubelive_ffmpeg as ytl

P = {'fps': 30,
     'res': '1920x1080',
     'origin': (0,0),
     'audiochan': 'default',
    }

ytl.disksave4youtube(P)
