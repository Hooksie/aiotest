import asyncio
import heapq
from collections import Counter
from collections import deque

class TestableHandle:
    """
    A testable Handle implementation
    """
    def __init__(self, when, callback, args):
        self.when = when
        self.callback = callback
        self.args = args

    def __lt__(self, other_task):
        return self.when < other_task.when


class TimeTravelingTestLoop(asyncio.AbstractEventLoop):
    """
    A testable PEP-3156 event loop implementation.  It does not
    support true network capabilities, but is capable of traveling
    forward in time in a deterministic manner.
    """
    def __init__(self):
        self.durations = Counter()
        #: A heap of all time-scheduled Handles
        self._scheduled = []
        #: A FIFO of ready-to-run Handles
        self._ready = deque()
        #: The current monotonic wall time, in seconds.
        self._wall = 591282000.0

    def time(self):
        """
        Returns the current time according to the event loop's clock. This may
        be time.time() or time.monotonic() or some other system-specific clock,
        but it must return a float expressing the time in units of
        approximately one second since some epoch.
        """
        return self._wall

    def advance(self, duration):
        """
        Advance the clock of the test loop. Any task that
        was scheduled to run during this time are executed
        in chronological order.

        Raises ValueError if ``duration`` is negative.
        """
        if duration < 0:
            raise ValueError("advance() must be given a positive duration")

        self._wall += duration

        if self._scheduled:
            # Pull out all scheduled events corresponding to the
            # current wall time, and place them on the ready FIFO.
            t = self._scheduled[0]
            while (t is not None) and (self._wall >= t.when):
                self._ready.append(t)
                heapq.heappop(self._scheduled)
                t = self._scheduled[0] if len(self._scheduled) else None

        # Execute all Handles on the ready FIFO.
        while self._ready:
            handle = self._ready.popleft()
            handle.callback(*handle.args)

    def call_later(self, delay, callback, *args):
        """
        Arrange for callback(*args) to be called approximately delay
        seconds in the future, once, unless cancelled.
        Returns a Handle representing the callback,
        whose cancel() method can be used to cancel the callback.

        Callbacks scheduled in the past or at exactly the same time will
        be called in an undefined order.
        """
        self.call_at(self.time() + delay, callback, *args)

    def call_at(self, when, callback, *args):
        """
        This is like call_later(), but the time is expressed as an
        absolute time. Returns a similar Handle.
        """
        # keep track of the callbacks and delays for each.
        task = TestableHandle(when, callback, args)
        # push the scheduled task onto the priority queue.
        heapq.heappush(self._scheduled, task)

    def call_soon(self, callback, *args):
        """
        This schedules a callback to be called as soon as possible.
        Returns a Handle (see below) representing the callback, whose cancel()
        method can be used to cancel the callback. It guarantees that callbacks
        are called in the order in which they were scheduled.
        """
        # All tasks are put at the end of the ready FIFO, immediately.
        # This guarantees that they will be called in order, as soon as possible.
        # when=0 because we don't care what the value is (already on the ready FIFO)
        handle = TestableHandle(0, callback, args)
        self._ready.append(handle)

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



