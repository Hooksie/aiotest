import asyncio
from unittest import TestCase as _TestCase

from aiotest.loop import TimeTravelingTestLoop


def format_call(coro, args):
    return "{func_name}({args})".format(func_name=coro.__name__, args=', '.join(repr(arg) for arg in args))


class TestCase(_TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.event_loop = TimeTravelingTestLoop()
        asyncio.set_event_loop(self.event_loop)

    def assertCoroResult(self, expected_value, coro, *args, msg=None, max_time=0):
        future = asyncio.async(coro(*args), loop=self.event_loop)
        self.event_loop.advance(max_time)
        if not future.done():
            self.failureException("coroutine did not complete within max time allowed.")
        actual_value = future.result()

        if actual_value != expected_value:
            if msg is None:
                raise self.failureException("{expected} != {actual} for {call}".format(
                    actual=actual_value,
                    expected=expected_value,
                    call=format_call(coro, args))
                )

            raise self.failureException(msg)

    def assertCoroNotResult(self, unexpected_value, coro, *args, msg=None, max_time=0):
        future = asyncio.async(coro(*args), loop=self.event_loop)
        self.event_loop.advance(max_time)
        if not future.done():
            self.failureException("coroutine did not complete within max time allowed.")
        actual_value = future.result()

        if actual_value == unexpected_value:
            if msg is None:
                raise self.failureException("{unexpected} == {actual} for {call}".format(
                    actual=actual_value,
                    unexpected=unexpected_value,
                    call=format_call(coro, args))
                )

            raise self.failureException(msg)

    def assertCoroDuration(self, duration, coro, *args, msg=None):
        future = asyncio.async(coro(*args), loop=self.event_loop)
        self.event_loop.advance(duration, inclusive=False)

        if future.done():
            self.failureException("coroutine completed too soon.")

        self.event_loop.advance(0, inclusive=True)

        if not future.done():
            if msg is None:
                raise self.failureException("coroutine did not complete within duration.")

            raise self.failureException(msg)
