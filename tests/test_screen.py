#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx
import subprocess

R = Path(__file__).parent
skip = False

sites = ['periscope', 'youtube', 'facebook']
inifn = R / 'test.ini'

S = pls.stream.Stream(inifn, 'localhost-test')
S.osparam()
timelimit = int(S.timelimit[1]) + 3   # allowing 3 seconds leeway
del S


def test_screenshare():
    S = pls.Screenshare(inifn, sites)
    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps == approx(30.)

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 1800


def test_screenshare_stream(listener):
    global skip
    S = pls.Screenshare(inifn, 'localhost-test')

    ok = S.check_device()

    if not ok:
        skip = True
        pytest.skip(f'device not available: {S.streams.popitem()[1].checkcmd}')

    S.golive()


def test_webcam_script(listener):
    if skip:
        pytest.skip(f'device not available')

    subprocess.check_call(['ScreenshareLivestream',
                           '-i', str(inifn),
                           'localhost-test', '--yes'],
                          timeout=timelimit)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
