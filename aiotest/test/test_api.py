import asyncio
from aiotest import TestCase


@asyncio.coroutine
def simple_add(a, b):
    return a + b


class BasicApiTests(TestCase):

    def test_simple_result(self):
        self.assertCoroResult(4, simple_add, 2, 2)

    def test_simple_result_incorrect(self):
        self.assertCoroNotResult(6, simple_add, 2, 2)

    def test_simple_message(self):
        msg = "What a terrible exception"
        try:
            self.assertCoroResult(4, simple_add, 2, 2, msg=msg)
        except TestCase.failureException as err:
            self.assertEqual(msg, str(err))
