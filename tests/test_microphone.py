#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
import subprocess

R = Path(__file__).parent
skip = False

sites = ['periscope', 'youtube', 'facebook']
inifn = R / 'test.ini'

LOGO = R.parent / 'doc' / 'logo.png'
IMG4K = R / 'check4k.png'

S = pls.stream.Stream(inifn, 'localhost-test')
S.osparam()
timelimit = int(S.timelimit[1]) + 3   # allowing 3 seconds leeway
del S


def test_microphone():
    S = pls.Microphone(inifn, sites,
                       image=LOGO)

    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps is None
        assert S.streams[s].res == (720, 540)

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 800


def test_microphone_4Kbg():
    S = pls.Microphone(inifn, sites,
                       image=IMG4K)

    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps is None
        assert S.streams[s].res == (3840, 2160)

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 4000


def test_microphone_stream(listener):
    global skip
    S = pls.Microphone(inifn, 'localhost-test', image=LOGO)

    ok = S.check_device()

    if not ok:
        skip = True
        pytest.skip(f'device not available: {S.streams.popitem()[1].checkcmd}')

    S.golive()


def test_microphone_script(listener):
    if skip:
        pytest.skip(f'device not available')

    subprocess.check_call(['MicrophoneLivestream',
                           '-i', str(inifn),
                           'localhost-test', '--yes'],
                          timeout=timelimit)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
