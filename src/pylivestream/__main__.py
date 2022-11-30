import signal
from argparse import ArgumentParser

from .api import (
    capture_screen,
    stream_webcam,
)


def screencapture():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser()
    p.add_argument("outfn", help="video file to save to disk.")
    p.add_argument("-i", "--ini", help="*.ini file with stream parameters")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    capture_screen(ini_file=P.ini, out_file=P.outfn, assume_yes=P.yes, timeout=P.timeout)


def webcam():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="livestream webcam")
    p.add_argument(
        "websites",
        help="site to stream, e.g. localhost youtube periscope facebook twitch",
        nargs="+",
    )
    p.add_argument("-i", "--ini", help="*.ini file with stream parameters")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    stream_webcam(ini_file=P.ini, websites=P.websites, assume_yes=P.yes, timeout=P.timeout)
