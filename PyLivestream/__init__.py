from pathlib import Path
from typing import List, Union, Dict
import logging
#
from . import stream
from . import utils

__all__ = ['FileIn', 'Microphone', 'SaveDisk', 'Screenshare', 'Webcam']


class Livestream(stream.Stream):

    def __init__(self,
                 ini: Path,
                 site: str, vidsource: str=None,
                 image: Path=None,
                 loop: bool=False,
                 infn: Path=None,
                 caption: str=None,
                 yes: bool=False) -> None:
        super().__init__(ini, site, vidsource, image, loop, infn,
                         caption=caption, yes=yes)

        self.site = site.lower()

        self.osparam()

        self.video_bitrate()

        vidIn: List[str] = self.videoIn()
        vidOut: List[str] = self.videoOut()

        audIn: List[str] = self.audioIn()
        audOut: List[str] = self.audioOut()

        buf: List[str] = self.buffer(self.server)
# %% begin to setup command line
        cmd: List[str] = []
        cmd.append(self.exe)

        cmd.extend(self.loglevel)
        cmd.extend(self.yes)
        cmd.extend(self.timelimit)

        cmd.extend(self.queue)

        cmd += vidIn + audIn

        if not self.movingimage:  # FIXME: need a different filter chain to caption moving images
            cmd += self.F.drawtext(self.caption)

        cmd += vidOut + audOut
        cmd += buf

        streamid: str = self.key if self.key else ''

        self.sink: List[str] = [self.server + streamid]

        self.cmd: List[str] = cmd + self.sink

    def startlive(self, sinks: List[str]=None):
        """finally start the stream(s)"""
        proc = None
# %% special cases for localhost tests
        if self.key is None:
            if self.site == 'localhost':
                proc = self.F.listener()  # start own RTMP server
            else:
                print('\n', ' '.join(self.cmd), '\n', flush=True)
                return
# %% RUN STREAM
        cmd: List[str]
        if not sinks:  # single stream
            utils.run(self.cmd)
        elif self.movingimage:
            if len(sinks) > 1:
                logging.warning(f'streaming only to {sinks[0]}')

            utils.run(self.cmd)
        elif len(sinks) == 1:
            utils.run(self.cmd)
        else:  # multi-stream output tee
            cmdstem: List[str] = self.cmd[:-3]
            # +global_header is necessary to tee to multiple services
            cmd = cmdstem + ['-flags:v', '+global_header',
                             '-f', 'tee']

            if self.image:
                #  connect image to video stream, audio file to audio stream
                cmd += ['-map', '0:v', '-map', '1:a']
            else:
                if self.vidsource == 'file':
                    # picks first video and audio stream, often correct
                    cmd += ['-map', '0:v', '-map', '0:a:0']
                else:  # device (webcam)
                    # connect video device to video stream,
                    # audio device to audio stream
                    cmd += ['-map', '0:v', '-map', '1:a']

            cmd += ['[f=flv]' + '|[f=flv]'.join(sinks)]  # no double quotes

            utils.run(cmd)

# %% this kill the listener before starting the next process, or upon final process closing.
        if proc is not None:
            proc.terminate()
        yield


# %% operators
class Screenshare(Livestream):

    def __init__(self,
                 ini: Path,
                 websites: Union[str, List[str]],
                 caption: str=None,
                 yes: bool=False) -> None:

        vidsource = 'screen'

        if isinstance(websites, str):
            websites = [websites]

        streams = {}
        for site in websites:
            streams[site] = Livestream(ini, site, vidsource,
                                       caption=caption, yes=yes)

        self.streams: Dict[str, Livestream] = streams

    def golive(self):

        sinks: List[str] = [self.streams[stream].sink[0]
                            for stream in self.streams]

        try:
            next(self.streams[unify_streams(self.streams)].startlive(sinks))
        except StopIteration:
            pass


class Webcam(Livestream):

    def __init__(self,
                 ini: Path,
                 websites: Union[str, List[str]],
                 caption: str=None,
                 yes: bool=False) -> None:

        vidsource = 'camera'

        if isinstance(websites, str):
            websites = [websites]

        streams = {}
        for site in websites:
            streams[site] = Livestream(ini, site, vidsource,
                                       caption=caption,  yes=yes)

        self.streams: Dict[str, Livestream] = streams

    def golive(self):

        sinks: List[str] = [self.streams[stream].sink[0]
                            for stream in self.streams]

        try:
            next(self.streams[unify_streams(self.streams)].startlive(sinks))
        except StopIteration:
            pass


class Microphone(Livestream):

    def __init__(self,
                 ini: Path,
                 sites: Union[str, List[str]],
                 image: Path,
                 caption: str=None,
                 yes: bool=False) -> None:

        if isinstance(sites, str):
            sites = [sites]

        streams = {}
        for site in sites:
            streams[site] = Livestream(ini, site, image=image,
                                       loop=True,
                                       caption=caption, yes=yes)

        self.streams: Dict[str, Livestream] = streams

    def golive(self):

        sinks: List[str] = [self.streams[stream].sink[0]
                            for stream in self.streams]

        try:
            next(self.streams[unify_streams(self.streams)].startlive(sinks))
        except StopIteration:
            pass


# %% File-based inputs
class FileIn(Livestream):

    def __init__(self,
                 ini: Path,
                 sites: Union[str, List[str]],
                 infn: Path,
                 loop: bool=False,
                 image: Path=None,
                 caption: str=None,
                 yes: bool=False) -> None:

        vidsource = 'file'

        if isinstance(sites, str):
            sites = [sites]

        streams = {}
        for site in sites:
            streams[site] = Livestream(ini, site, vidsource, image=image,
                                       loop=loop, infn=infn,
                                       caption=caption, yes=yes)

        self.streams: Dict[str, Livestream] = streams

    def golive(self):

        sinks: List[str] = [self.streams[stream].sink[0]
                            for stream in self.streams]

        try:
            next(self.streams[unify_streams(self.streams)].startlive(sinks))
        except StopIteration:
            pass


class SaveDisk(stream.Stream):

    def __init__(self,
                 ini: Path, outfn: Path=None,
                 caption: str=None,
                 yes: bool=False) -> None:
        """
        records to disk screen capture with audio

        if not outfn, just cite command that would have run
        """
        site = 'file'
        vidsource = 'screen'

        super().__init__(ini, site, vidsource, caption=caption)

        self.outfn = Path(outfn).expanduser() if outfn else None

        self.osparam()

        vidIn: List[str] = self.videoIn()
        vidOut: List[str] = self.videoOut()

        audIn: List[str] = self.audioIn()
        audOut: List[str] = self.audioOut()

        self.cmd: List[str] = [str(self.exe)]
        self.cmd += vidIn + audIn
        self.cmd += vidOut + audOut

        # ffmpeg relies on suffix for container type, this is a fallback.
        if self.outfn and not self.outfn.suffix:
            self.cmd += ['-f', 'flv']

        self.cmd += [str(self.outfn)]

#        if sys.platform == 'win32':  # doesn't seem to be needed.
#            cmd += ['-copy_ts']

    def save(self):

        if self.outfn:
            utils.run(self.cmd)

        else:
            print('specify filename to save screen capture w/ audio to disk.')


def unify_streams(streams: Dict[str, stream.Stream]) -> str:
    """
    find least common denominator stream settings,
        so "tee" output can generate multiple streams.
    First try: use stream with lowest video bitrate.

    Exploits that Python >= 3.6 has guaranteed dict() ordering.

    fast native Python argmin()
    https://stackoverflow.com/a/11825864
    """
    vid_bw: List[int] = [streams[s].video_kbps for s in streams]

    argmin: int = min(range(len(vid_bw)), key=vid_bw.__getitem__)

    key: str = list(streams.keys())[argmin]

    return key
