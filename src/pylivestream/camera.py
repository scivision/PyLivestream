import signal
import argparse

from .api import stream_webcam


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = argparse.ArgumentParser(description="livestream webcam")
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
