#!/usr/bin/env python
from pathlib import Path
import PyLivestream

rdir = Path(__file__).parent

inifn =  rdir/'test.ini'
sites = ['periscope','youtube','facebook','twitch','mixer','ustream','vimeo']


def test_screenshare():

    S = PyLivestream.Screenshare(inifn, sites)
    for s in S.streams:
        if s.site == 'periscope':
            assert s.video_kbps == 800
        else:
            assert s.video_kbps == 1800




def test_webcam():

    S = PyLivestream.Webcam(inifn, sites)
    for s in S.streams:
        if s.site == 'periscope':
            assert s.video_kbps == 800
        else:
            if int(s.res[1]) == 480:
                assert s.video_kbps == 500
            elif int(s.res[1]) == 720:
                assert s.video_kbps == 1800


def test_loop():
    for s in sites:
        p = PyLivestream.FileIn(inifn,s, rdir/'star_collapse_out.avi')

        if s == 'periscope':
            assert p.stream.video_kbps == 800
        else:
            if p.stream.res is None:
                continue

            if int(p.stream.res[1]) == 480:
                assert p.stream.video_kbps == 500
            elif int(p.stream.res[1]) == 720:
                assert p.stream.video_kbps == 1800


def test_disk():
    for s in sites:
        p = PyLivestream.SaveDisk(inifn, '')
        assert p.site == 'file'
        assert p.video_kbps == 3000



if __name__ == '__main__':
    test_screenshare()
    test_webcam()
    test_loop()
    test_disk()