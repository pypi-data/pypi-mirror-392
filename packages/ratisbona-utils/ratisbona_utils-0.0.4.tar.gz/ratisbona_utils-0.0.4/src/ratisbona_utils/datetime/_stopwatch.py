"""
    This module contains utility functions for time dependent operations.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, TypeVar

@dataclass
class Stopwatch:
    """
    Class helpful to time operations.

    best use it with a with-statement like:
    ```python
        with Stopwatch() as stopwatch:
            do_something_expensive

        stopwatch.time_elapsed_millis # now contains elapsed time in milliseconds
        print(stopwatch) # prints nicely formatted timeing information.
    ```

    Another good way of using it is the with_stopwatch_do wrapper:

    ```python
        stopwatch = Stopwatch()
        expensive_function = with_stopwatch(expensive_function, stopwatch)
        expensive_function()
    ```
    """
    is_counting: bool = False
    time_elapsed_millis: int = 0
    last_advanced: datetime = None
    show_msec: bool = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self) -> None:
        """
        Starts the stopwatch
        """
        self.is_counting = True
        self.last_advanced = None
        self.advance()

    def stop(self) -> None:
        """
        Stops the stopwatch. You may restart it using `start()` in which case the
        times will add up!
        """
        self.advance()
        self.is_counting = False
        self.last_advanced = None

    def toggle(self) -> None:
        """
        Toggles the state of the stopwatch. If it is counting it will stop and vice versa.
        """
        if self.is_counting:
            self.stop()
        else:
            self.start()

    def reset(self):
        """
        Resets the stopwatch to zero. It will also stop counting if it was counting at the time of reset.
        So don't forget to call `start()` if you want to continue counting.
        """
        old_is_counting = self.is_counting
        self.is_counting = False
        self.time_elapsed_millis = False
        self.last_advanced = None
        self.is_counting = old_is_counting
        self.advance()

    def __str__(self):
        """
        Returns a nicely formatted string with the elapsed time.
        Format of the String is: `HH:MM:SS.mmm` where `HH` is hours, `MM` is minutes, `SS` is seconds and `mmm` is milliseconds.
        If `show_msec` is set to `False` the milliseconds part will be omitted.
        """
        raw_secs, milliseconds = divmod(self.time_elapsed_millis, 1000)
        raw_min, seconds = divmod(raw_secs, 60)
        hours, minutes = divmod(raw_min, 60)

        retval = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        if self.show_msec:
            retval += f".{milliseconds:03d}"

        return retval

    def advance(self):
        """
        Advances the time by the time that has passed since the last advance.
        Call it, if you want to have a in between-reading before stopping the clock.
        """
        if not self.is_counting:
            return
        the_now = datetime.now()
        if self.last_advanced:
            difference = the_now - self.last_advanced
            self.time_elapsed_millis += difference.microseconds // 1000
        self.last_advanced = the_now


T = TypeVar('T')


def with_stopwatch(a_callable: Callable[..., T], stopwatch: Stopwatch) -> Callable[..., T]:
    """
    Wraps a function with a stopwatch. The stopwatch will be started before the function is called and stopped afterwards.

    :param a_callable: The function to wrap.
    :param stopwatch: The stopwatch to use.
    :return: The wrapped function.
    """
    def with_stopwatch_do(*args, **kwargs) -> T:

        with stopwatch:
            return a_callable(*args, **kwargs)

    return with_stopwatch_do
