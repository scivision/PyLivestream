import signal
from argparse import ArgumentParser
import typing as T

from .base import FileIn, Microphone, Screenshare, SaveDisk, Webcam
from .glob import fileglob, playonce


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

    S = FileIn(P.ini, P.websites, infn=P.infn, loop=True, yes=P.yes, timeout=P.timeout)
    sites: T.List[str] = list(S.streams.keys())
    # %% Go live
    if P.yes:
        print(f"going live on {sites} looping file {P.infn}")
    else:
        input(f"Press Enter to go live on {sites}," f"looping file {P.infn}")
        print("Or Ctrl C to abort.")

    S.golive()


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

    s = Microphone(P.ini, P.websites, image=P.image, yes=P.yes, timeout=P.timeout)
    sites = list(s.streams.keys())
    # %% Go live
    if P.yes:
        print("going live on", sites)
    else:
        input(f"Press Enter to go live on {sites}.    Or Ctrl C to abort.")

    s.golive()


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

    S = Screenshare(P.ini, P.websites, yes=P.yes, timeout=P.timeout)
    sites: T.List[str] = list(S.streams.keys())
    # %% Go live
    if P.yes:
        print("going live on", sites)
    else:
        input(f"Press Enter to go live on {sites}    Or Ctrl C to abort.")

    S.golive()


def screencapture():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = ArgumentParser()
    p.add_argument("outfn", help="video file to save to disk.")
    p.add_argument("-i", "--ini", help="*.ini file with stream parameters")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    s = SaveDisk(P.ini, P.outfn, yes=P.yes, timeout=P.timeout)
    # %%
    if P.yes:
        print("saving screen capture to", s.outfn)
    else:
        input(f"Press Enter to screen capture to file {s.outfn}" "Or Ctrl C to abort.")

    s.save()


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

    S = Webcam(P.ini, P.websites, yes=P.yes, timeout=P.timeout)
    sites: T.List[str] = list(S.streams.keys())
    # %% Go live
    if P.yes:
        print("going live on", sites)
    else:
        input(f"Press Enter to go live on {sites}.    Or Ctrl C to abort.")

    S.golive()


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
    # %% file / glob wranging
    flist = fileglob(P.path, P.glob)

    print("streaming these files. Be sure list is correct! \n")
    print("\n".join(map(str, flist)))
    print()

    if P.yes:
        print("going live on", P.websites)
    else:
        input(f"Press Enter to go live on {P.websites}.    Or Ctrl C to abort.")

    usemeta = P.nometa

    if P.loop:
        while True:
            playonce(flist, P.image, P.websites, P.ini, P.shuffle, usemeta, P.yes)
    else:
        playonce(flist, P.image, P.websites, P.ini, P.shuffle, usemeta, P.yes)
