#!/usr/bin/env python
from pathlib import Path
import PyLivestream

rdir = Path(__file__).parent

inifn = rdir / 'test.ini'

sites = ['periscope','youtube','facebook','twitch']

def test_screenshare():
    for s in sites:
        PyLivestream.Screenshare(inifn, s)



def test_webcam():
    for s in sites:
        PyLivestream.Webcam(inifn, s)


def test_loop():
    for s in sites:
        PyLivestream.FileIn(inifn,s,'')



if __name__ == '__main__':
    test_screenshare()

    test_webcam()

    test_loop()