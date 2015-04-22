import unittest
import asyncio

from aiotest import loop

class TimeTravelingTestLoopTest(unittest.TestCase):
    def setUp(self):
        self.f = asyncio.Future()
        self.event_loop = loop.TimeTravelingTestLoop()

    def test_task_init(self):
        t = loop.TestableHandle(1.5, print, [1,2,3])
        self.assertEqual(1.5, t.delay)
        self.assertEqual(print, t.callback)
        self.assertEqual([1, 2, 3], t.args)

    def test_task_order_lt(self):
        t1 = loop.TestableHandle(1.5, print, [1, 2, 3])
        t2 = loop.TestableHandle(2.0, print, [1, 2, 3])

        self.assertTrue(t1 < t2)
        self.assertFalse(t2 < t1)

    def test_schedule_dont_run(self):
        """
        A callback scheduled via call_later should not execute if
        time has not advanced.
        """
        self.event_loop.call_later(5.0, self.f.set_result, 5643)
        self.assertFalse(self.f.done(), "Callback should not have been executed.")

    def test_schedule_dont_run_after_advance(self):
        """
        A callback scheduled via call_later should not execute if
        the minimum amount of time has not yet advanced.
        """
        self.event_loop.call_later(5.0, self.f.set_result, 5643)
        self.event_loop.advance(4.0)
        self.assertFalse(self.f.done(), "Callback should not have been executed.")

    def test_schedule_run_after_advance(self):
        """
        A callback scheduled via call_later should execute if
        the minimum amount of time has advanced.
        """
        self.event_loop.call_later(5.0, self.f.set_result, 5643)
        self.event_loop.advance(6.0)
        self.assertTrue(self.f.done(), "Callback should have been executed.")
        self.assertEqual(5643, self.f.result())

    def test_schedule_two_run_after_advance(self):
        """
        If multiple callbacks are scheduled out-of-order, only the callback
        whose time as expired should execute.
        """
        f = asyncio.Future()
        g = asyncio.Future()
        self.event_loop.call_later(5.0, f.set_result, 5643)
        self.event_loop.call_later(4.0, g.set_result, 1234)
        self.event_loop.advance(4.5)
        self.assertFalse(f.done(), "First callback should not have been executed.")
        self.assertTrue(g.done(), "Second callback should have been executed.")
        self.assertEqual(1234, g.result())

    def test_schedule_advance_run_in_order(self):
        """
        If multiple callbacks are scheduled out-of-order, and multiple
        would have been called in the time advance()'d, they should
        be executed in chronological order.
        """
        exec_order_list = []

        self.event_loop.call_later(5.0, exec_order_list.append, 5643)
        self.event_loop.call_later(4.0, exec_order_list.append, 1234)
        self.event_loop.call_later(4.5, exec_order_list.append, 2057)
        self.event_loop.advance(6.0)

        self.assertEqual([1234, 2057, 5643], exec_order_list)

    def tes