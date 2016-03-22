import asyncio
import heapq


class TestableHandle:
    """
    A testable Handle implementation
    """
    def __init__(self, when, callback, args):
        self.when = when
        self.callback = callback
        self.args = args
        self.cancelled = False

    def __lt__(self, other_task):
        return self.when < other_task.when

    def cancel(self):
        """
        Cancel this handle, preventing it from being executed later.
        """
        self.cancelled = True

class TimeTravelingTestLoop(asyncio.base_events.BaseEventLoop):
    """
    A testable PEP-3156 event loop implementation.  It does not
    support true network capabilities, but is capable of traveling
    forward in time in a deterministic manner.
    """
    def __init__(self):
        super().__init__()

        # self.durations = Counter()
        #: A heap of all time-scheduled Handles
        # self._scheduled = []
        #: A FIFO of ready-to-run Handles
        # self._ready = deque()
        #: The current monotonic wall time, in seconds.
        self._wall = 591282000.0
        #: When specific coroutines last yielded to the event loop.
        self._call_calender = {}

    def _run_once(self):
        """
        Run a "single iteration" of the event loop.

        Really, we're going to just run everything that can be run at this exact
        moment in time.
        """
        self.advance(0)

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

        # The time on the wall clock we want to be at when
        # we finish advancing.
        travel_to = self._wall + duration

        # Because we're moving through time, we cant assume that our first check in the scheduled heap
        # will reveal everything that would occur before our travel_to time.  That's because we may, for example,
        # exhaust our scheduled heap, only for tasks to introduce new items to it while they're being run.  Those
        # new items might be under our travel_to time.
        #
        # Once we reach a point where our _ready queue is empty, we know we won't be adding anything back
        # into the schedule, and we can safely get out.
        while True:
            if self._scheduled:
                # Pull out all scheduled events corresponding to the
                # current wall time, and place them on the ready FIFO.
                t = self._scheduled[0]

                # We move ahead to each scheduled task that happens before our
                # total advance duration has passed.
                while (t is not None) and (travel_to >= t._when):
                    # Don't bother putting canceled tasks on the ready FIFO.
                    if not t._cancelled:
                        self._ready.append(t)
                    heapq.heappop(self._scheduled)
                    t = self._scheduled[0] if len(self._scheduled) else None

            if self._ready:
                # Execute all non-cancelled Handles on the ready FIFO.
                while self._ready:
                    handle = self._ready.popleft()
                    try:
                        self._wall = handle._when
                    except AttributeError:
                        # Not all handles will have a _when, and that's OK.
                        pass

                    if not handle._cancelled:
                        handle._run()

            # We now know there's nothing that could be added back into our schedule.
            else:
                break

        # Make sure that we've caught up to exactly the point in time we want to be.
        # aka: make sure the wall clock is set right when we've advanced past our latest scheduled
        # task.
        self._wall = travel_to

    def call_soon_threadsafe(self, callback, *args):
        """
        Like call_soon(callback, *args) , but when called from another thread
        while the event loop is blocked waiting for I/O,  unblocks
        the event loop.

        NOTE: This testable event loop is not meant to be called from
        multiple threads, so this is a synonym for call_soon().
        Unit tests should not be written to use threads to avoid
        non-deterministic behavior - YMMV!
        """
        return self.call_soon(callback, *args)


    # Missing mandatory APIs from PEP 3156:
    # -----
    #
    # run_forever()
    # run_until_complete()
    # stop()
    # is_running()
    # close()
    #
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



