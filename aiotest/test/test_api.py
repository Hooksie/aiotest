import asyncio
from aiotest import TestCase
import unittest


@asyncio.coroutine
def simple_add(a, b):
    return a + b


class BasicApiTests(TestCase):

    def test_assert_coro_result(self):
        self.assertCoroResult(4, simple_add, 2, 2)

    def test_assert_coro_result_incorrect(self):
        with self.assertRaises(TestCase.failureException):
            self.assertCoroResult(20, simple_add, 2, 2)

    def test_assert_coro_not_result(self):
        self.assertCoroNotResult(20, simple_add, 2, 2)

    def test_assert_coro_not_result_incorrect(self):
        with self.assertRaises(TestCase.failureException):
            self.assertCoroNotResult(4, simple_add, 2, 2)

    def test_simple_message(self):
        msg = "What a terrible exception"
        try:
            self.assertCoroResult(4, simple_add, 2, 2, msg=msg)
        except TestCase.failureException as err:
            self.assertEqual(msg, str(err))

    @unittest.skip("Doesn't do yet.")
    def test_assert_coro_duration(self):

        @asyncio.coroutine
        def takes_5_seconds():
            yield from asyncio.sleep(5)

        self.assertCoroDuration(5, takes_5_seconds())

    @unittest.skip("Doesn't do yet.")
    def test_assert_coro_duration_incorrect(self):

        @asyncio.coroutine
        def takes_10_seconds():
            yield from asyncio.sleep(10)

        with self.assertRaises(self.failureException):
            self.assertCoroDuration(5, takes_10_seconds())
