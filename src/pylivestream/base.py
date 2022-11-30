from __future__ import annotations
from pathlib import Path
import logging
import os
import typing

from .stream import Stream
from .utils import run, check_device

__all__ = ["FileIn", "Microphone", "SaveDisk", "Screenshare", "Camera"]


class Livestream(Stream):
    def __init__(self, inifn: Path, site: str, **kwargs) -> None:
        super().__init__(inifn, site, **kwargs)

        self.site = site.lower()

        self.osparam(inifn)

        self.docheck = kwargs.get("docheck")

        self.video_bitrate()

        vidIn: list[str] = self.videoIn()
        vidOut: list[str] = self.videoOut()

        audIn: list[str] = self.audioIn()
        audOut: list[str] = self.audioOut()

        buf: list[str] = self.buffer()
        # %% begin to setup command line
        cmd: list[str] = []
        cmd.append(self.exe)

        cmd += self.loglevel
        cmd += self.yes

        #        cmd += self.timelimit  # terminate input after N seconds, IF specified

        cmd += self.queue

        cmd += vidIn + audIn

        if not self.movingimage:  # FIXME: need a different filter chain to caption moving images
            cmd += self.F.drawtext(self.caption)

        cmd += vidOut + audOut
        cmd += buf

        cmd.extend(self.timelimit)  # terminate output after N seconds, IF specified

        streamid = self.streamid if hasattr(self, "streamid") else ""
        # cannot have double quotes for Mac/Linux,
        #    but need double quotes for Windows
        sink: str = self.url + "/" + streamid
        if os.name == "nt":
            sink = '"' + sink + '"'

        self.sink = sink
        cmd.append(sink)

        self.cmd: list[str] = cmd
        # %% quick check command, to verify device exists
        # 0.1 seems OK, spurious buffer error on Windows that wasn't helped by any bigger size
        CHECKTIMEOUT = "0.1"

        self.checkcmd: list[str] = (
            [self.exe]
            + self.loglevel
            + ["-t", CHECKTIMEOUT]
            + self.videoIn(quick=True)
            + self.audioIn(quick=True)
            + ["-t", CHECKTIMEOUT]
            + ["-f", "null", "-"]  # camera needs at output
        )

    def startlive(self, sinks: list[str] = None):
        """
        start the stream(s)
        """

        if self.docheck:
            self.check_device()

        proc = None
        # %% special cases for localhost tests
        if self.site == "localhost-test":
            pass
        elif self.site == "localhost":
            proc = self.F.listener()  # start own RTMP server

        if proc is not None and proc.poll() is not None:
            # listener stopped prematurely, probably due to error
            raise RuntimeError(f"listener stopped with code {proc.poll()}")
        # %% RUN STREAM
        if not sinks:  # single stream
            run(self.cmd)
        elif self.movingimage:
            if len(sinks) > 1:
                logging.warning(f"streaming only to {sinks[0]}")

            run(self.cmd)
        elif len(sinks) == 1:
            run(self.cmd)
        else:  # multi-stream output tee
            cmdstem: list[str] = self.cmd[:-3]
            # +global_header is necessary to tee to multiple services
            cmd: list[str] = cmdstem + ["-flags:v", "+global_header", "-f", "tee"]

            if self.image:
                #  connect image to video stream, audio file to audio stream
                cmd += ["-map", "0:v", "-map", "1:a"]
            else:
                if self.vidsource == "file":
                    # picks first video and audio stream, often correct
                    cmd += ["-map", "0:v", "-map", "0:a:0"]
                else:  # device (Camera)
                    # connect video device to video stream,
                    # audio device to audio stream
                    cmd += ["-map", "0:v", "-map", "1:a"]

            # cannot have double quotes for Mac/Linux,
            #    but need double quotes for Windows
            if os.name == "nt":
                sink = f'"[f=flv]{sinks[0][1:-1]}'
                for s in sinks[1:]:
                    sink += f"|[f=flv]{s[1:-1]}"
                sink += '"'
            else:
                sink = f"[f=flv]{sinks[0]}"
                for s in sinks[1:]:
                    sink += f"|[f=flv]{s}"

            cmd.append(sink)

            run(cmd)

        # %% stop the listener before starting the next process, or upon final process closing.
        if proc is not None and proc.poll() is None:
            proc.terminate()
        yield

    def check_device(self, site: str = None) -> bool:
        """
        requires stream to have been configured first.
        does a quick test stream to "null" to verify device is actually accessible
        """
        if not site:
            try:
                site = self.site
            except AttributeError:
                site = list(self.streams.keys())[0]  # type: ignore

        try:
            checkcmd = self.checkcmd
        except AttributeError:
            checkcmd = self.streams[site].checkcmd  # type: ignore

        return check_device(checkcmd)


# %% operators
class Screenshare:
    def __init__(self, inifn: Path, websites: list[str], **kwargs) -> None:

        if isinstance(websites, str):
            websites = [websites]

        streams = {}
        for site in websites:
            streams[site] = Livestream(inifn, site, vidsource="screen", **kwargs)

        self.streams: typing.Mapping[str, Livestream] = streams

    def golive(self) -> None:

        sinks: list[str] = [self.streams[stream].sink for stream in self.streams]

        try:
            next(self.streams[unify_streams(self.streams)].startlive(sinks))
        except StopIteration:
            pass


class Camera:
    def __init__(self, inifn: Path, websites: list[str], **kwargs):

        if isinstance(websites, str):
            websites = [websites]

        streams = {}
        for site in websites:
            streams[site] = Livestream(inifn, site, vidsource="camera", **kwargs)

        self.streams: dict[str, Livestream] = streams

    def golive(self) -> None:

        sinks: list[str] = [self.streams[stream].sink for stream in self.streams]

        try:
            next(self.streams[unify_streams(self.streams)].startlive(sinks))
        except StopIteration:
            pass


class Microphone:
    def __init__(self, inifn: Path, websites: list[str], **kwargs):

        if isinstance(websites, str):
            websites = [websites]

        streams = {}
        for site in websites:
            streams[site] = Livestream(inifn, site, **kwargs)

        self.streams: dict[str, Livestream] = streams

    def golive(self) -> None:

        sinks: list[str] = [self.streams[stream].sink for stream in self.streams]

        try:
            next(self.streams[unify_streams(self.streams)].startlive(sinks))
        except StopIteration:
            pass


# %% File-based inputs
class FileIn:
    def __init__(self, inifn: Path, websites: str | list[str], **kwargs):

        if isinstance(websites, str):
            websites = [websites]

        streams = {}
        for site in websites:
            streams[site] = Livestream(inifn, site, vidsource="file", **kwargs)

        self.streams: dict[str, Livestream] = streams

    def golive(self) -> None:

        sinks: list[str] = [self.streams[stream].sink for stream in self.streams]

        try:
            next(self.streams[unify_streams(self.streams)].startlive(sinks))
        except StopIteration:
            pass


class SaveDisk(Stream):
    def __init__(self, inifn: Path, outfn: Path = None, **kwargs):
        """
        records to disk screen capture with audio

        if not outfn, just cite command that would have run
        """
        super().__init__(inifn, site="file", vidsource="screen", **kwargs)

        self.outfn = Path(outfn).expanduser() if outfn else None

        self.osparam(inifn)

        vidIn: list[str] = self.videoIn()
        vidOut: list[str] = self.videoOut()

        audIn: list[str] = self.audioIn()
        audOut: list[str] = self.audioOut()

        self.cmd: list[str] = [str(self.exe)]
        self.cmd += vidIn + audIn
        self.cmd += vidOut + audOut

        # ffmpeg relies on suffix for container type, this is a fallback.
        if self.outfn and not self.outfn.suffix:
            self.cmd += ["-f", "flv"]

        self.cmd += [str(self.outfn)]

    #        if sys.platform == 'win32':  # doesn't seem to be needed.
    #            cmd += ['-copy_ts']

    def save(self):

        if self.outfn:
            run(self.cmd)

        else:
            print("specify filename to save screen capture w/ audio to disk.")


def unify_streams(streams: typing.Mapping[str, Stream]) -> str:
    """
    find least common denominator stream settings,
        so "tee" output can generate multiple streams.
    First try: use stream with lowest video bitrate.

    Exploits that Python has guaranteed dict() ordering.

    fast native Python argmin()
    https://stackoverflow.com/a/11825864
    """
    vid_bw: list[int] = [streams[s].video_kbps for s in streams]

    argmin: int = min(range(len(vid_bw)), key=vid_bw.__getitem__)

    key: str = list(streams.keys())[argmin]

    return key
