import signal
import argparse

from .api import stream_file


if __name__ == "__main__":
    """
    LIVE STREAM using FFMPEG -- Looping input file endlessly

    NOTE: for audio files,
        use FileGlob2Livestream.py with options `-image myimg.jpg -loop`

    https://www.scivision.dev/youtube-live-ffmpeg-livestream/
    https://support.google.com/youtube/answer/2853702
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = argparse.ArgumentParser(description="Livestream a single looped input file")
    p.add_argument("infn", help="file to stream, looping endlessly.")
    p.add_argument(
        "websites",
        help="site to stream, e.g. localhost youtube facebook twitch",
        nargs="+",
    )
    p.add_argument("json", help="JSON file with stream parameters such as key")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    stream_file(
        ini_file=P.json,
        websites=P.websites,
        assume_yes=P.yes,
        timeout=P.timeout,
        loop=True,
        video_file=P.infn,
    )
