from typing import List, Union


class Ffmpeg():

    def __init__(self):

        self.ERROR: List[str] = ['-v', 'error']
        self.WARNING: List[str] = ['-v', 'warning']
        self.INFO: List[str] = ['-v', 'info']

        self.YES: List[str] = ['-y']

        # default 8, increasing can help avoid warnings
        self.QUEUE: List[str] = ['-thread_queue_size', '8']

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
