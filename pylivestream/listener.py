""" this is necessary for pytest when console scripts are called via subprocess in unit test.
The style in FFMPEG won't work for test and vice versa."""
import pytest
import subprocess


@pytest.fixture()
def listener():
    """needed for pytest, regular function doesn't terminate properly under test"""
    print('starting RTMP listener')
    proc = subprocess.Popen(['ffplay', '-v', 'fatal', '-timeout', '5',
                             '-autoexit', 'rtmp://localhost'],
                            stdout=subprocess.DEVNULL)

    yield proc
    proc.terminate()
