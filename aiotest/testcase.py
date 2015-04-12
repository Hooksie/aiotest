import asyncio
from unittest import TestCase as _TestCase

from aiotest.testloop import TestEventLoop


class TestCase(_TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.event_loop = TestEventLoop()

    def assertCoroResult(self, expected_value, coro, *args, msg=None):
        actual_value = self.event_loop.run_until_complete(coro(*args))

        if actual_value != expected_value:
            if msg is not None:
                raise self.failureException("{actual} != {expected}".format(actual=actual_value, expected=expected_value))

            raise self.failureException(msg)

    def assertCoroNotResult(self, unexpected_value, coro, *args, msg=None):
        actual_value = self.event_loop.run_until_complete(coro(*args))

        if actual_value == unexpected_value:
            if msg is None:
                raise self.failureException("{actual} == {unexpected}".format(actual=actual_value, unexpected=unexpected_value))

            raise self.failureException(msg)

    def assertCoroDuration(self, duration, coro):
        self.event_loop.run_until_complete(coro)
        duration = self.event_loop.min_time_of(coro)

        # duration > ????? > Profit?


