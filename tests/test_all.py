#!/usr/bin/env python
from pathlib import Path
import numpy
import PyLivestream

rdir = Path(__file__).parent

inifn =  rdir/'test.ini'
sites = ['periscope','youtube','facebook','twitch','mixer','ustream','vimeo']


def test_screenshare():
    for s in sites:
        PyLivestream.Screenshare(inifn, s)


def test_webcam():
    for s in sites:
        PyLivestream.Webcam(inifn, s)


def test_loop():
    for s in sites:
        PyLivestream.FileIn(inifn,s, rdir/'star_collapse_out.avi')


def test_disk():
    for s in sites:
        PyLivestream.SaveDisk(inifn, '')


if __name__ == '__main__':
    numpy.testing.run_module_suite()