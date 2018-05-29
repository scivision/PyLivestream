from pathlib import Path
import subprocess as sp
#
from .stream import Stream


class Livestream(Stream):

    def __init__(self,ini:Path, site:str, vidsource:str, image:bool=False, loop:bool=False, infn:Path=None):
        super().__init__(ini,site,vidsource,image,loop,infn)

        self.site = site.lower()

        self.osparam()

        self.video_bitrate()

        vid1,vid2 = self.videostream()

        aud1 = self.audiostream()
        aud2 = self.audiocomp()

        buf = self.buffer()

        cmd = [self.exe] + vid1 + aud1 + vid2 + aud2 + buf

        streamid = self.key if self.key else ''

        self.sink = [self.server + streamid]

        self.cmd = cmd + self.sink


    def golive(self, sinks:list=None):
        """finally start the stream(s)"""

        if self.key is None:
            print('\n',' '.join(self.cmd),'\n')
            return

        if not sinks: # single stream
            print('\n',' '.join(self.cmd))
            sp.check_call(self.cmd)
        else: # multi-stream output tee
            cmdstem = self.cmd[:-3]
            # +global_header is necessary to tee to Periscope (and other services at same time)
            cmd = cmdstem + ['-flags:v','+global_header',
                             '-f','tee','-map','0:v','-map','1:a']
            cmd += ['[f=flv]'+'|[f=flv]'.join(sinks)] # no double quotes
            print(' '.join(cmd))

            sp.check_call(cmd)



# %% operators
class Screenshare(Livestream):

    def __init__(self, ini:Path, sites:list):

        vidsource = 'screen'

        if isinstance(sites,str):
            sites = [sites]

        self.streams = []
        self.sites = []
        for site in sites:
            stream = Livestream(ini,site,vidsource)
            if stream.key:
                self.streams.append(stream)
                self.sites.append(site)

        if not self.streams:
            raise ValueError('No valid stream key files or keys were found in {}'.format(ini))


    def golive(self):

        sinks = [stream.sink[0] for stream in self.streams]

        self.streams[self.unify_streams(self.streams)].golive(sinks)


class Webcam(Livestream):

    def __init__(self, ini:Path, sites:list):

        vidsource = 'camera'

        if isinstance(sites,str):
            sites = [sites]

        self.streams = []
        self.sites = []
        for site in sites:
            stream = Livestream(ini,site,vidsource)
            if stream.key:
                self.streams.append(stream)
                self.sites.append(site)

        if not self.streams:
            raise ValueError('No valid stream key files or keys were found in {}'.format(ini))


    def golive(self):

        sinks = [stream.sink[0] for stream in self.streams]

        self.streams[self.unify_streams(self.streams)].golive(sinks)


class FileIn(Livestream):

    def __init__(self, ini:Path, site:str, infn:Path, loop:bool=False, image:bool=False):

        vidsource = 'file'

        self.stream = Livestream(ini, site, vidsource, image, loop, infn)


    def golive(self):
        self.stream.golive()


class SaveDisk(Stream):

    def __init__(self, ini:Path, outfn:Path=None, clobber:bool=False):
        """
        records to disk screen capture with audio

        if not outfn, just cite command that would have run
        """
        site = 'file'
        vidsource = 'screen'

        super().__init__(ini,site,vidsource)

        self.outfn = Path(outfn).expanduser() if outfn else None

        self.osparam()

        vid1,vid2 = self.videostream()

        aud1 = self.audiostream()
        aud2 = self.audiocomp()

        self.cmd = [self.exe] + vid1 + aud1 + vid2 + aud2

        if self.outfn and not self.outfn.suffix:  # ffmpeg relies on suffix for container type, this is a fallback.
            self.cmd += ['-f','flv']

        self.cmd += [str(self.outfn)]

        if self.timelimit:
            self.cmd += ['-timelimit',self.timelimit]

        if clobber:
            self.cmd += ['-y']

#        if sys.platform == 'win32':
#            cmd += ['-copy_ts']

    def save(self):

        print('\n',' '.join(self.cmd),'\n')

        if self.outfn:
            try:
                ret = sp.check_call(self.cmd)
                print('FFmpeg returncode',ret)
            except FileNotFoundError:
                pass
        else:
            print('specify filename to save screen capture with audio to disk.')
