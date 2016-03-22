import asyncio
from aiotest import TestCase


@asyncio.coroutine
def simple_add(a, b):
    return a + b


class BasicApiTests(TestCase):

    def test_assert_coro_result(self):
        self.assertCoroResult(4, simple_add, 2, 2)

    def test_assert_coro_result_incorrect(self):
        with self.assertRaises(TestCase.failureException) as context:
            self.assertCoroResult(20, simple_add, 2, 2)

        self.assertEqual(str(context.exception), '20 != 4 for simple_add(2, 2)')

    def test_assert_coro_not_result(self):
        self.assertCoroNotResult(20, simple_add, 2, 2)

    def test_assert_coro_not_result_incorrect(self):
        with self.assertRaises(TestCase.failureException) as context:
            self.assertCoroNotResult(4, simple_add, 2, 2)

        self.assertEqual(str(context.exception), '4 == 4 for simple_add(2, 2)')

    def test_assert_coro_not_result_custom_message(self):
        msg = "What a terrible exception"
        with self.assertRaises(TestCase.failureException) as context:
            self.assertCoroResult(5, simple_add, 2, 2, msg=msg)

        self.assertEqual(str(context.exception), msg)

    def test_assert_coro_duration(self):

        @asyncio.coroutine
        def takes_5_seconds():
            yield from asyncio.sleep(5, loop=self.event_loop) # FIXME Shouldn't need to specify loop.

        self.assertCoroDuration(5, takes_5_seconds)

    def test_assert_coro_duration_incorrect(self):

        @asyncio.coroutine
        def takes_10_seconds():
            yield from asyncio.sleep(10, loop=self.event_loop) # FIXME Shouldn't need to specify loop.

        with self.assertRaises(TestCase.failureException):
            self.assertCoroDuration(5, takes_10_seconds)
