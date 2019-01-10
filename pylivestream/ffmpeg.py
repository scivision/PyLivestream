import subprocess
from typing import List, Union
from time import sleep
import os
from pathlib import Path


class Ffmpeg():

    def __init__(self):

        self.ERROR = ['-v', 'error']
        self.WARNING = ['-v', 'warning']
        self.INFO = ['-v', 'info']

        self.YES = ['-y']

        # default 8, increasing can help avoid warnings
        self.QUEUE = ['-thread_queue_size', '8']

        self.THROTTLE = '-re'

    def timelimit(self, t: Union[str, int, float]) -> List[str]:
        if t is None:
            return []

        assert isinstance(t, (str, int, float))

        t = str(t)

        if len(t) > 0:
            return ['-t', str(t)]
        else:
            return []

    def drawtext(self, text: str = None) -> List[str]:
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
        -timeout 1 is necessary to avoid instant error, since stream starts after the listener.
        I put -timeout 5 to allow for very slow computers.
        -timeout is the delay to wait for stream input before erroring.
        """
        print('starting RTMP listener.  Press   q   in this terminal to end stream.')

        proc = subprocess.Popen(['ffplay', '-v', 'fatal',
                                 '-timeout', '5',
                                 '-autoexit', 'rtmp://localhost'])
#        proc = subprocess.Popen(['ffmpeg', '-v', 'fatal', '-timeout', '5',
#                                 '-i', 'rtmp://localhost', '-f', 'null', '-'],
#                                stdout=subprocess.DEVNULL)

        sleep(0.5)  # 0.2 not long enough. 0.3 worked, so set 0.5 for some margin.

        return proc

    def movingBG(self, bgfn: Path = None) -> List[str]:
        if not bgfn:
            return []

        bg = str(bgfn)
        if os.name == 'nt':
            bg = bg.replace('\\', '/')   # for PureWindowsPath

        return ['-filter_complex', f'movie={bg}:loop=0,setpts=N/FRAME_RATE/TB']
