#!/usr/bin/env python
from pathlib import Path
import os
import unittest
import PyLivestream

rdir = Path(__file__).parent
os.chdir(str(rdir))

inifn =  'test.ini'
sites = ['periscope','youtube','facebook','twitch','mixer','ustream','vimeo']

class BasicTests(unittest.TestCase):
    def test_screenshare(self):
        for s in sites:
            try:
                PyLivestream.Screenshare(inifn, s)
            except FileNotFoundError:
                pass

    def test_webcam(self):
        for s in sites:
            try:
                PyLivestream.Webcam(inifn, s)
            except FileNotFoundError:
                pass


    def test_loop(self):
        for s in sites:
            try:
                PyLivestream.FileIn(inifn,s, 'star_collapse_out.avi')
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    unittest.main()
