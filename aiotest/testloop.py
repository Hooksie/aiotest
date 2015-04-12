import asyncio
from collections import Counter


class TimeTravelingTestLoop(asyncio.BaseEventLoop):

    def __init__(self):
        super().__init__()

        self.durations = Counter()

    def call_later(self, delay, callback, *args):
        print("Dependency injection?")

    # FIXME This signature is going to change imminently.  We probably cant do this with the coro.
    def min_time_of(self, coro):
        return 0


# FIXME Chances are good this is a bad idea
default_loop = asyncio.get_event_loop().__class__

class TestEventLoop(default_loop, TimeTravelingTestLoop):
    pass



