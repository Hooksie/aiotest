import asyncio
import heapq
from collections import Counter


class TestableHandle:
    """
    A testable Handle implementation
    """
    def __init__(self, delay, callback, args):
        self.delay = delay
        self.callback = callback
        self.args = args

    def __lt__(self, other_task):
        return self.delay < other_task.delay


class TimeTravelingTestLoop(asyncio.AbstractEventLoop):
    """
    A testable PEP-3156 event loop implementation.  It does not
    support true network capabilities, but is capable of traveling
    forward in time in a deterministic manner.
    """
    def __init__(self):
        self.durations = Counter()
        self._scheduled = []

    def advance(self, duration):
        """
        Advance the clock of the test loop. Any task that
        was scheduled to run during this time are executed
        in chronological order.
        """
        if self._scheduled:
            t = self._scheduled[0]
            while (t is not None) and (duration > t.delay):
                t.callback(*t.args)
                heapq.heappop(self._scheduled)
                t = self._scheduled[0] if len(self._scheduled) else None

    def call_later(self, delay, callback, *args):
        """
        Arrange for callback(*args) to be called approximately delay
        seconds in the future, once, unless cancelled.
        Returns a Handle representing the callback,
        whose cancel() method can be used to cancel the callback.

        Callbacks scheduled in the past or at exactly the same time will
        be called in an undefined order.
        """
        # keep track of the callbacks and delays for each.
        task = TestableHandle(delay, callback, args)
        # push the scheduled task onto the priority queue.
        heapq.heappush(self._scheduled, task)

    # FIXME This signature is going to change imminently.  We probably cant do this with the coro.
    def min_time_of(self, coro):
        return 0

    # Missing mandatory APIs from PEP 3156:
    # -----
    #
    # run_forever()
    # run_until_complete()
    # stop()
    # is_running()
    # close()
    #
    # call_soon()
    # call_at()
    # time()
    #
    # call_soon_threadsafe()
    # run_in_executor()
    # set_default_executor()
    # getaddrinfo()
    # getnameinfo()
    #
    # create_connection()
    # create_server()
    # create_datagram_endpoint()
    #
    # sock_recv()
    # sock_sendall()
    # sock_connect()
    # sock_accept()

#
# # FIXME Chances are good this is a bad idea
# default_loop = asyncio.get_event_loop().__class__

class TestEventLoop(asyncio.SelectorEventLoop, TimeTravelingTestLoop):
    pass



