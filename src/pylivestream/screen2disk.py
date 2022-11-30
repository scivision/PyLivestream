import signal
from argparse import ArgumentParser

from .api import capture_screen


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser()
    p.add_argument("outfn", help="video file to save to disk.")
    p.add_argument("json", help="JSON file with stream parameters such as key")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    capture_screen(ini_file=P.json, out_file=P.outfn, assume_yes=P.yes, timeout=P.timeout)
