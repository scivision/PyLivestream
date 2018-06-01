from pathlib import Path
from typing import List, Union, Dict
#
from . import stream
from . import sio

__all__ = ['FileIn', 'Microphone', 'SaveDisk', 'Screenshare', 'Webcam']


class Livestream(stream.Stream):

    def __init__(self, ini: Path, site: str, vidsource: str=None,
                 image: Path=None, loop: bool=False, infn: Path=None,
                 yes: bool=False) -> None:
        super().__init__(ini, site, vidsource, image, loop, infn, yes=yes)

        self.site = site.lower()

        self.osparam()

        self.video_bitrate()

        vid1, vid2 = self.videostream()

        aud1: List[str] = self.audiostream()
        aud2: List[str] = self.audiocomp()

        buf: List[str] = self.buffer(self.server)
# %% begin to setup command line
        cmd: List[str] = []
        cmd.append(self.exe)

        cmd.extend(self.loglevel)
        cmd.extend(self.yes)
        cmd.extend(self.timelimit)
        cmd.extend(self.queue)

        cmd += vid1 + aud1 + vid2 + aud2 + buf

        streamid: str = self.key if self.key else ''

        self.sink: List[str] = [self.server + streamid]

        self.cmd: List[str] = cmd + self.sink

    def startlive(self, sinks: List[str]=None):
        """finally start the stream(s)"""

        if self.key is None and self.server not in ('rtmp://localhost',
                                                    'NUL', '/dev/null'):
            print('\n', ' '.join(self.cmd), '\n')
            return

        if not sinks:  # single stream
            sio.run(self.cmd)
        else:  # multi-stream output tee
            cmdstem = self.cmd[:-3]
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

            sio.run(cmd)


# %% operators
class Screenshare(Livestream):

    def __init__(self, ini: Path, websites: Union[str, List[str]],
                 yes: bool=False) -> None:

        vidsource = 'screen'

        if isinstance(websites, str):
            websites = [websites]

        streams = {}
        for site in websites:
            streams[site] = Livestream(ini, site, vidsource, yes=yes)

        self.streams: Dict[str, Livestream] = streams

    def golive(self):

        sinks: List[str] = [self.streams[stream].sink[0]
                            for stream in self.streams]

        self.streams[unify_streams(self.streams)].startlive(sinks)


class Webcam(Livestream):

    def __init__(self, ini: Path, websites: Union[str, List[str]],
                 yes: bool=False) -> None:

        vidsource = 'camera'

        if isinstance(websites, str):
            websites = [websites]

        streams = {}
        for site in websites:
            streams[site] = Livestream(ini, site, vidsource, yes=yes)

        self.streams: Dict[str, Livestream] = streams

    def golive(self):

        sinks: List[str] = [self.streams[stream].sink[0]
                            for stream in self.streams]

        self.streams[unify_streams(self.streams)].startlive(sinks)


class Microphone(Livestream):

    def __init__(self, ini: Path, sites: Union[str, List[str]], image: Path,
                 yes: bool=False) -> None:

        if isinstance(sites, str):
            sites = [sites]

        streams = {}
        for site in sites:
            streams[site] = Livestream(ini, site, image=image, yes=yes)

        self.streams: Dict[str, Livestream] = streams

    def golive(self):

        sinks: List[str] = [self.streams[stream].sink[0]
                            for stream in self.streams]

        self.streams[unify_streams(self.streams)].startlive(sinks)


# %% File-based inputs
class FileIn(Livestream):

    def __init__(self, ini: Path, sites: Union[str, List[str]], infn: Path,
                 loop: bool=False, image: Path=None, yes: bool=False) -> None:

        vidsource = 'file'

        if isinstance(sites, str):
            sites = [sites]

        streams = {}
        for site in sites:
            streams[site] = Livestream(ini, site, vidsource, image=image,
                                       loop=loop, infn=infn, yes=yes)

        self.streams: Dict[str, Livestream] = streams

    def golive(self):

        sinks: List[str] = [self.streams[stream].sink[0]
                            for stream in self.streams]

        self.streams[unify_streams(self.streams)].startlive(sinks)


class SaveDisk(stream.Stream):

    def __init__(self, ini: Path, outfn: Path=None, yes: bool=False) -> None:
        """
        records to disk screen capture with audio

        if not outfn, just cite command that would have run
        """
        site = 'file'
        vidsource = 'screen'

        super().__init__(ini, site, vidsource)

        self.outfn = Path(outfn).expanduser() if outfn else None

        self.osparam()

        vid1, vid2 = self.videostream()

        aud1 = self.audiostream()
        aud2 = self.audiocomp()

        self.cmd: List[str] = [str(self.exe)] + vid1 + aud1 + vid2 + aud2

        # ffmpeg relies on suffix for container type, this is a fallback.
        if self.outfn and not self.outfn.suffix:
            self.cmd += ['-f', 'flv']

        self.cmd += [str(self.outfn)]

#        if sys.platform == 'win32':  # doesn't seem to be needed.
#            cmd += ['-copy_ts']

    def save(self):

        if self.outfn:
            sio.run(self.cmd)

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
