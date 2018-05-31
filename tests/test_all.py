#!/usr/bin/env python
from pathlib import Path
import PyLivestream
import unittest

rdir = Path(__file__).parent

inifn = rdir/'test.ini'
sites = ['periscope', 'youtube', 'facebook']


class Tests(unittest.TestCase):
    def test_screenshare(self):

        S = PyLivestream.Screenshare(inifn, sites)
        for s in S.streams:
            if s == 'periscope':
                assert S.streams[s].video_kbps == 800
            else:
                assert S.streams[s].video_kbps == 1800

    def test_webcam(self):

        S = PyLivestream.Webcam(inifn, sites)
        for s in S.streams:
            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                if int(S.streams[s].res[1]) == 480:
                    assert S.streams[s].video_kbps == 500
                elif int(S.streams[s].res[1]) == 720:
                    assert S.streams[s].video_kbps == 1800

    def test_filein_video(self):
        S = PyLivestream.FileIn(inifn, sites, rdir/'star_collapse_out.avi')
        for s in S.streams:
            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                if int(S.streams[s].res[1]) == 480:
                    self.assertEqual(S.streams[s].video_kbps, 500)
                elif int(S.streams[s].res[1]) == 720:
                    self.assertEqual(S.streams[s].video_kbps, 1800)

    def test_filein_audio(self):
        flist = list(rdir.glob('*.ogg'))

        S = PyLivestream.FileIn(inifn, sites, flist[0])
        for s in S.streams:
            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 500)

    def test_microphone(self):
        S = PyLivestream.Microphone(inifn, sites,
                                    rdir.parent / 'doc' / 'logo.png')

        for s in S.streams:
            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 500)

    def test_disk(self):
        for s in sites:
            p = PyLivestream.SaveDisk(inifn, '')
            assert p.site == 'file'
            assert p.video_kbps == 3000

    def test_stream(self):
        """stream to NUL"""

        s = PyLivestream.FileIn(inifn, 'localhost',
                                rdir / 'orch_short.ogg',
                                image=rdir.parent / 'doc' / 'logo.png',
                                yes=True)
        s.golive()


if __name__ == '__main__':
    unittest.main()
