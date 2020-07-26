import signal
from argparse import ArgumentParser

from .api import (
    stream_microphone,
    stream_file,
    stream_files,
    stream_screen,
    capture_screen,
    stream_webcam,
)


def loop_file():
    """
    LIVE STREAM using FFMPEG -- Looping input file endlessly

    NOTE: for audio files,
        use FileGlob2Livestream.py with options `-image myimg.jpg -loop`

    https://www.scivision.dev/youtube-live-ffmpeg-livestream/
    https://support.google.com/youtube/answer/2853702
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="Livestream a single looped input file")
    p.add_argument("infn", help="file to stream, looping endlessly.")
    p.add_argument(
        "websites",
        help="site to stream, e.g. localhost youtube periscope facebook twitch",
        nargs="+",
    )
    p.add_argument("-i", "--ini", help="*.ini file with stream parameters")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    stream_file(
        ini_file=P.ini,
        websites=P.websites,
        assume_yes=P.yes,
        timeout=P.timeout,
        loop=True,
        video_file=P.infn,
    )


def microphone():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="livestream microphone audio")
    p.add_argument(
        "websites",
        help="site to stream, e.g. localhost youtube periscope facebook twitch",
        nargs="+",
    )
    p.add_argument("-image", help="static image to display.")
    p.add_argument("-i", "--ini", help="*.ini file with stream parameters")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    stream_microphone(
        ini_file=P.ini,
        websites=P.websites,
        assume_yes=P.yes,
        timeout=P.timeout,
        still_image=P.image,
    )


def screenshare():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="livestream screenshare")
    p.add_argument(
        "websites",
        help="site to stream, e.g. localhost youtube periscope facebook twitch",
        nargs="+",
    )
    p.add_argument("-i", "--ini", help="*.ini file with stream parameters")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    stream_screen(ini_file=P.ini, websites=P.websites, assume_yes=P.yes, timeout=P.timeout)


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


def glob_run():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser(description="Livestream a globbed input file list")
    p.add_argument("path", help="path to discover files from")
    p.add_argument(
        "websites",
        help="site to stream, e.g. localhost youtube periscope facebook twitch",
        nargs="+",
    )
    p.add_argument("-glob", help="file glob pattern to stream.")
    p.add_argument("-i", "--ini", help="*.ini file with stream parameters")
    p.add_argument("-image", help="static image to display, for audio-only files.")
    p.add_argument("-shuffle", help="shuffle the globbed file list", action="store_true")
    p.add_argument("-loop", help="repeat the globbed file list endlessly", action="store_true")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-nometa", help="do not add metadata caption to video", action="store_false")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    stream_files(
        ini_file=P.ini,
        websites=P.websites,
        assume_yes=P.yes,
        timeout=P.timeout,
        loop=P.loop,
        video_path=P.path,
        glob=P.glob,
        shuffle=P.shuffle,
        still_image=P.image,
        no_meta=P.nometa,
    )
