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
        if isinstance(t, (str, int, float)):
            return ['-t', str(t)]
        else:
            return []
