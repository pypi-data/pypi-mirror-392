import unittest
from time import sleep

from ratisbona_utils.datetime import Stopwatch, with_stopwatch


class TestStopWatch(unittest.TestCase):

    def test_spending_time_must_advance_clock(self):

        # Given
        stopwatch = Stopwatch()
        watched_sleep = with_stopwatch(sleep, stopwatch)

        # When
        watched_sleep(0.1)

        # Then
        self.assertGreater(stopwatch.time_elapsed_millis, 90)
        print(stopwatch)

    def test_stopwatch_must_not_run_after_watched_function_terminates(self):
        # Given
        stopwatch = Stopwatch()
        watched_sleep = with_stopwatch(sleep, stopwatch)

        # When
        watched_sleep(0.1)
        sleep(1.0)

        # Then
        self.assertGreater(stopwatch.time_elapsed_millis, 90)
        self.assertLess(stopwatch.time_elapsed_millis, 110)

    def test_stopwatch_must_resume_on_multiple_invocations(self):
        # Given
        stopwatch = Stopwatch()
        watched_sleep = with_stopwatch(sleep, stopwatch)

        # When
        watched_sleep(0.1)
        sleep(0.5)
        watched_sleep(0.1)

        # Then
        self.assertGreater(stopwatch.time_elapsed_millis, 180)
        self.assertLess(stopwatch.time_elapsed_millis, 230)
        print(stopwatch)

    def test_suspending_the_clock_must_not_advance_time(self):
        with Stopwatch() as stopwatch:
            sleep(0.1)
            stopwatch.stop()
            sleep(1.0)
            stopwatch.start()
            sleep(0.1)
        self.assertGreater(stopwatch.time_elapsed_millis, 180)
        self.assertLess(stopwatch.time_elapsed_millis, 220)


if __name__ == '__main__':
    unittest.main()
