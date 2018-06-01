#!/usr/bin/env python
from pathlib import Path
import PyLivestream as pls
import pytest
import unittest
import subprocess
import logging
import os

CI = os.environ['CI'] if 'CI' in os.environ else False

rdir = Path(__file__).resolve().parent  # .resolve() is necessary
DEVNULL = subprocess.DEVNULL

inifn = rdir/'test.ini'
sites = ['periscope', 'youtube', 'facebook']

VIDFN = rdir / 'star_collapse_out.avi'


@pytest.fixture(scope='function')
def listener():
    """
    no need to check return code, errors will show up in client.
    """
    print('starting RTMP listener')
    proc = subprocess.Popen(['ffmpeg', '-v', 'fatal', '-timeout', '5',
                             '-i', 'rtmp://localhost', '-f', 'null', '-'],
                            stdout=DEVNULL)

    yield proc
    proc.terminate()  # after all tests done


@pytest.mark.usefixtures("listener")
class Tests(unittest.TestCase):

    def test_key(self):
        """tests reading of stream key"""
        self.assertEqual(pls.sio.getstreamkey('abc123'), 'abc123')
        self.assertEqual(pls.sio.getstreamkey(rdir / 'periscope.key'),
                         'abcd1234')
        self.assertEqual(pls.sio.getstreamkey(''), None)
        self.assertEqual(pls.sio.getstreamkey(None), None)
        self.assertEqual(pls.sio.getstreamkey(rdir), None)

    def test_exe(self):
        exe, pexe = pls.sio.getexe()
        self.assertIn('ffmpeg', exe)
        self.assertIn('ffprobe', pexe)

        for p in (None, '', 'ffmpeg'):
            exe, pexe = pls.sio.getexe(p)
            self.assertIn('ffmpeg', exe)
            self.assertIn('ffprobe', pexe)

    def test_attrs(self):
        for p in (None, '',):
            self.assertEqual(pls.sio.get_resolution(p), None)

        self.assertEqual(pls.sio.get_resolution(VIDFN), (720, 480))
        self.assertEqual(pls.sio.get_framerate(VIDFN), 25.0)

    def test_screenshare(self):

        S = pls.Screenshare(inifn, sites)
        for s in S.streams:
            self.assertNotIn('-re', S.streams[s].cmd)
            self.assertEqual(S.streams[s].fps, 30.)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 1800)

    def test_webcam(self):

        S = pls.Webcam(inifn, sites)
        for s in S.streams:
            self.assertNotIn('-re', S.streams[s].cmd)
            self.assertEqual(S.streams[s].fps, 30.)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                if int(S.streams[s].res[1]) == 480:
                    assert S.streams[s].video_kbps == 500
                elif int(S.streams[s].res[1]) == 720:
                    assert S.streams[s].video_kbps == 1800

    def test_filein_video(self):
        S = pls.FileIn(inifn, sites, VIDFN)
        for s in S.streams:
            self.assertIn('-re', S.streams[s].cmd)
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
            self.assertIn('-re', S.streams[s].cmd)
            self.assertEqual(S.streams[s].fps, None)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 500)

    def test_microphone(self):
        S = pls.Microphone(inifn, sites,
                           image=rdir.parent / 'doc' / 'logo.png')

        for s in S.streams:
            self.assertNotIn('-re', S.streams[s].cmd)
            self.assertEqual(S.streams[s].fps, None)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 500)
# %% try to stream, XFAIL on CI because no hardware.
        try:
            S.golive()
        except subprocess.CalledProcessError as e:
            logging.warning(f'Microphone test skipped due to {e}')

    @pytest.mark.skipif(CI, reason="Many CI's don't have audio hardware")
    def test_microphone_script(self):
        subprocess.check_call(['python',
                               'MicrophoneLivestream.py',
                               '-i', str(inifn),
                               'localhost', '--yes'],
                              stdout=DEVNULL, timeout=8,
                              cwd=rdir.parent)

    def test_disk(self):
        for s in sites:
            p = pls.SaveDisk(inifn, '')
            self.assertEqual(p.site, 'file')
            self.assertEqual(p.video_kbps, 3000)

    @pytest.mark.skipif(CI, reason="Many CI's don't allow opening ports")
    def test_stream(self):
        """stream to localhost"""
        s = pls.FileIn(inifn, 'localhost',
                       rdir / 'orch_short.ogg',
                       image=rdir.parent / 'doc' / 'logo.png',
                       yes=True)
        s.golive()


if __name__ == '__main__':
    # Tests().test_microphone_script()

    pytest.main()
