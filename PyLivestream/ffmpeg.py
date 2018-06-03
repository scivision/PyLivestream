import subprocess
from typing import List, Union
from time import sleep
import os
from pathlib import Path


class Ffmpeg():

    def __init__(self):

        self.ERROR: List[str] = ['-v', 'error']
        self.WARNING: List[str] = ['-v', 'warning']
        self.INFO: List[str] = ['-v', 'info']

        self.YES: List[str] = ['-y']

        # default 8, increasing can help avoid warnings
        self.QUEUE: List[str] = ['-thread_queue_size', '8']

        self.THROTTLE: str = '-re'

    def timelimit(self, t: Union[None, str, int, float]) -> List[str]:
        if t is None:
            return []

        assert isinstance(t, (str, int, float))

        t = str(t)

        if len(t) > 0:
            return ['-t', str(t)]
        else:
            return []

    def drawtext(self, text: Union[None, str]) -> List[str]:
        # fontfile=/path/to/font.ttf:
        if not text:  # None or '' or [] etc.
            return []

        fontcolor = 'fontcolor=white'
        fontsize = 'fontsize=24'
        box = 'box=1'
        boxcolor = 'boxcolor=black@0.5'
        border = 'boxborderw=5'
        x = 'x=(w-text_w)/2'
        y = 'y=(h-text_h)*3/4'

        return ['-vf',
                f"drawtext=text='{text}':{fontcolor}:{fontsize}:{box}:{boxcolor}:{border}:{x}:{y}"]

    def listener(self):
        """
        no need to check return code, errors will show up in client.
        """
        print('starting RTMP listener')
        proc = subprocess.Popen(['ffplay', '-v', 'fatal', '-timeout', '5',
                                 '-autoexit', 'rtmp://localhost'],
                                stdout=subprocess.DEVNULL)
#        proc = subprocess.Popen(['ffmpeg', '-v', 'fatal', '-timeout', '5',
#                                 '-i', 'rtmp://localhost', '-f', 'null', '-'],
#                                stdout=subprocess.DEVNULL)

        sleep(0.5)  # 0.2 not long enough. 0.3 worked, so set 0.5 for some margin.
        return proc

    def movingBG(self, bgfn: Union[None, Path]) -> List[str]:
        assert isinstance(bgfn, Path)

        bg: str = str(bgfn)
        if os.name == 'nt':
            bg = bg.replace('\\', '/')   # for PureWindowsPath

        return ['-filter_complex', f'movie={bg}:loop=0,setpts=N/FRAME_RATE/TB']
