"""
This is no longer necessary due to PyLivestream improvements
"""

import pytest
import subprocess


@pytest.fixture(scope="function")
def listener():
    """needed for pytest, regular function doesn't terminate properly under test"""
    print("starting RTMP listener")
    proc = subprocess.Popen(
        ["ffplay", "-v", "fatal", "-timeout", "5", "-autoexit", "rtmp://localhost"],
        stdout=subprocess.DEVNULL,
    )

    yield proc
    proc.terminate()
