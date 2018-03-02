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
        PyLivestream.Screenshare(inifn, s)


def test_webcam():
    for s in sites:
        PyLivestream.Webcam(inifn, s)


def test_loop():
    for s in sites:
        PyLivestream.FileIn(inifn,s, 'star_collapse_out.avi')


def test_disk():
    for s in sites:
        PyLivestream.SaveDisk(inifn, '')