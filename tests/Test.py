#!/usr/bin/env python
from pathlib import Path
import os
import PyLivestream

rdir = Path(__file__).parent
os.chdir(str(rdir))

inifn =  'test.ini'

sites = ['periscope','youtube','facebook','twitch','mixer','ustream','vimeo']

def test_screenshare():
    for s in sites:
        try:
            PyLivestream.Screenshare(inifn, s)
        except FileNotFoundError:
            pass

def test_webcam():
    for s in sites:
        try:
            PyLivestream.Webcam(inifn, s)
        except FileNotFoundError:
            pass


def test_loop():
    for s in sites:
        try:
            PyLivestream.FileIn(inifn,s, 'star_collapse_out.avi')
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    test_screenshare()

    test_webcam()

    test_loop()
