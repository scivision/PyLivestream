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
