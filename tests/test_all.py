#!/usr/bin/env python
from pathlib import Path
import PyLivestream as pls
import unittest

rdir = Path(__file__).parent

inifn = rdir/'test.ini'
sites = ['periscope', 'youtube', 'facebook']


class Tests(unittest.TestCase):

    def test_key(self):
        """tests reading of stream key"""
        self.assertEqual(pls.sio.getstreamkey('abc123'), 'abc123')
        self.assertEqual(pls.sio.getstreamkey(rdir/'periscope.key'), 'abcd1234')
        self.assertEqual(pls.sio.getstreamkey(''), None)
        self.assertEqual(pls.sio.getstreamkey(None), None)
        self.assertEqual(pls.sio.getstreamkey(rdir), None)

    def test_screenshare(self):

        S = pls.Screenshare(inifn, sites)
        for s in S.streams:
            self.assertEqual(S.streams[s].fps, 30.)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 1800)

    def test_webcam(self):

        S = pls.Webcam(inifn, sites)
        for s in S.streams:
            self.assertEqual(S.streams[s].fps, 30.)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                if int(S.streams[s].res[1]) == 480:
                    assert S.streams[s].video_kbps == 500
                elif int(S.streams[s].res[1]) == 720:
                    assert S.streams[s].video_kbps == 1800

    def test_filein_video(self):
        S = pls.FileIn(inifn, sites, rdir/'star_collapse_out.avi')
        for s in S.streams:
            self.assertEqual(S.streams[s].fps, 25.)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                if int(S.streams[s].res[1]) == 480:
                    self.assertEqual(S.streams[s].video_kbps, 500)
                elif int(S.streams[s].res[1]) == 720:
                    self.assertEqual(S.streams[s].video_kbps, 1800)

    def test_filein_audio(self):
        flist = list(rdir.glob('*.ogg'))

        S = pls.FileIn(inifn, sites, flist[0])
        for s in S.streams:
            self.assertEqual(S.streams[s].fps, None)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 500)

    def test_microphone(self):
        S = pls.Microphone(inifn, sites,
                                    rdir.parent / 'doc' / 'logo.png')

        for s in S.streams:
            self.assertEqual(S.streams[s].fps, None)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 500)

    def test_disk(self):
        for s in sites:
            p = pls.SaveDisk(inifn, '')
            assert p.site == 'file'
            assert p.video_kbps == 3000

    def test_stream(self):
        """stream to NUL"""

        s = pls.FileIn(inifn, 'localhost',
                                rdir / 'orch_short.ogg',
                                image=rdir.parent / 'doc' / 'logo.png',
                                yes=True)
        s.golive()


if __name__ == '__main__':
    unittest.main()
