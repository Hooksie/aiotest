import unittest
import asyncio

from aiotest import loop

class TestableHandleTest(unittest.TestCase):
    """
    Test the TestableHandle implementation.
    """
    def test_task_init(self):
        """
        Test initializing the internal data of the TestableHandle,
        including capturing arguments.
        """
        t = loop.TestableHandle(1.5, print, [1,2,3])
        self.assertEqual(1.5, t.when)
        self.assertEqual(print, t.callback)
        self.assertEqual([1, 2, 3], t.args)

    def test_task_order_lt(self):
        """
        Ensure __lt__ works as expected.
        """
        t1 = loop.TestableHandle(1.5, print, [1, 2, 3])
        t2 = loop.TestableHandle(2.0, print, [1, 2, 3])

        self.assertTrue(t1 < t2)
        self.assertFalse(t2 < t1)

class TimeTravelingTestLoopTest(unittest.TestCase):
    def setUp(self):
        self.f = asyncio.Future()
        self.event_loop = loop.TimeTravelingTestLoop()

    def test_call_later_dont_run(self):
        """
        A callback scheduled via call_later should not execute if
        time has not advanced.
        """
        self.event_loop.call_later(5.0, self.f.set_result, 5643)
        self.assertFalse(self.f.done(), "Callback should not have been executed.")

    def test_call_later_dont_run_after_advance(self):
        """
        A callback scheduled via call_later should not execute if
        the minimum amount of time has not yet advanced.
        """
        self.event_loop.call_later(5.0, self.f.set_result, 5643)
        self.event_loop.advance(4.0)
        self.assertFalse(self.f.done(), "Callback should not have been executed.")

    def test_call_later_run_after_advance(self):
        """
        A callback scheduled via call_later should execute if
        the minimum amount of time has advanced.
        """
        self.event_loop.call_later(5.0, self.f.set_result, 5643)
        self.event_loop.advance(6.0)
        self.assertTrue(self.f.done(), "Callback should have been executed.")
        self.assertEqual(5643, self.f.result())

    def test_call_later_two_run_after_advance(self):
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

    def test_call_later_advance_run_in_order(self):
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

    def test_time_advance(self):
        """
        Ensure time() and advance() interact correctly.
        """
        start = self.event_loop.time()
        self.event_loop.advance(5.0)
        self.assertEqual(start + 5.0, self.event_loop.time())
        self.event_loop.advance(2.0)
        self.assertEqual(start + 7.0, self.event_loop.time())

    def test_time_advance_invalid(self):
        """
        Ensure advance() of a negative value raises ValueError,
        and the event loop time() is not affected.
        """
        start = self.event_loop.time()
        self.assertRaises(ValueError, self.event_loop.advance, -5.0)
        self.assertEqual(start, self.event_loop.time())

    def test_call_at_not_run(self):
        """
        Advancing the wall clock before a scheduled call_at should not
        cause this task to being run.
        """
        time = self.event_loop.time()
        event_list = []

        self.event_loop.call_at(time + 1.0, event_list.append, 1)
        self.event_loop.advance(0.5)

        self.assertEqual([], event_list)

    def test_call_at_advance_run(self):
        """
        Advancing the wall clock after a scheduled call_at should
        cause this task to be run.
        """
        time = self.event_loop.time()
        event_list = []

        self.event_loop.call_at(time + 1.0, event_list.append, 1)
        self.event_loop.advance(1.5)

        self.assertEqual([1], event_list)

    def test_call_at_advance_run_exact(self):
        """
        Advancing the wall clock to the exact scheduled time should
        cause this task to be run.
        """
        time = self.event_loop.time()
        event_list = []

        self.event_loop.call_at(time + 1.0, event_list.append, 1)
        self.event_loop.advance(1.0)

        self.assertEqual([1], event_list)

    def test_call_at_and_later_advance_run_in_order(self):
        """
        If multiple callbacks are scheduled, mixing call_later() and call_at(),
        and multiple would have been called in the time advance()'d,
        they should be executed in chronological order.
        """
        exec_order_list = []

        self.event_loop.call_later(5.0, exec_order_list.append, 5643)
        self.event_loop.call_later(4.0, exec_order_list.append, 1234)
        self.event_loop.call_later(4.5, exec_order_list.append, 2057)
        self.event_loop.call_at(self.event_loop.time() + 6.0, exec_order_list.append, 667)

        self.event_loop.advance(6.0)

        self.assertEqual([1234, 2057, 5643, 667], exec_order_list)