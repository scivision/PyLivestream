#!/usr/bin/env python
from pathlib import Path
import PyLivestream as pls
import pytest
import unittest
import subprocess
import logging

rdir = Path(__file__).parent

inifn = rdir/'test.ini'
sites = ['periscope', 'youtube', 'facebook']


@pytest.fixture(scope='function')
def listener():
    """
    no need to check return code, errors will show up in client.
    """
    print('starting RTMP listener')
    subprocess.Popen(['ffmpeg','-timeout', '5',
                          '-i', 'rtmp://localhost', '-f', 'null', '-'],
                     stdout=subprocess.DEVNULL)


class Tests(unittest.TestCase):


    def test_key(self):
        """tests reading of stream key"""
        self.assertEqual(pls.sio.getstreamkey('abc123'), 'abc123')
        self.assertEqual(pls.sio.getstreamkey(rdir / 'periscope.key'),
                         'abcd1234')
        self.assertEqual(pls.sio.getstreamkey(''), None)
        self.assertEqual(pls.sio.getstreamkey(None), None)
        self.assertEqual(pls.sio.getstreamkey(rdir), None)

    def test_screenshare(self):

        S = pls.Screenshare(inifn, sites)
        for s in S.streams:
            assert '-re' not in S.streams[s].cmd
            self.assertEqual(S.streams[s].fps, 30.)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 1800)

    def test_webcam(self):

        S = pls.Webcam(inifn, sites)
        for s in S.streams:
            assert '-re' not in S.streams[s].cmd
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
            assert '-re' in S.streams[s].cmd
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
            assert '-re' in S.streams[s].cmd
            self.assertEqual(S.streams[s].fps, None)

            if s == 'periscope':
                self.assertEqual(S.streams[s].video_kbps, 800)
            else:
                self.assertEqual(S.streams[s].video_kbps, 500)

    @pytest.mark.usefixtures("listener")
    def test_microphone(self):
        S = pls.Microphone(inifn, sites,
                           rdir.parent / 'doc' / 'logo.png')

        for s in S.streams:
            assert '-re' not in S.streams[s].cmd
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

    @pytest.mark.usefixtures("listener")
    def test_microphone_script(self):
        try:
            subprocess.check_call(['python', 'MicrophoneLivestream.py',
                                   'localhost', '--yes'], timeout=5)
        except subprocess.CalledProcessError as e:
            logging.warning(f'Microphone test skipped due to {e}')
        except subprocess.TimeoutExpired:
            logging.info('Microphone script test seems to have passed.')

    def test_disk(self):
        for s in sites:
            p = pls.SaveDisk(inifn, '')
            assert p.site == 'file'
            assert p.video_kbps == 3000

    @pytest.mark.usefixtures("listener")
    def test_stream(self):
        """stream to localhost"""

        s = pls.FileIn(inifn, 'localhost',
                       rdir / 'orch_short.ogg',
                       image=rdir.parent / 'doc' / 'logo.png',
                       yes=True)
        s.golive()


if __name__ == '__main__':
    unittest.main()
