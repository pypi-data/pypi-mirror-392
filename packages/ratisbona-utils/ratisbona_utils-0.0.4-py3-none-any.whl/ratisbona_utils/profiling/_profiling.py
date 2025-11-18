from dataclasses import dataclass
from typing import Callable, TypeVar, ContextManager, Optional

from ratisbona_utils.datetime import format_ms_HHMMSSss, Stopwatch

T = TypeVar("T")
Action = str
Milliseconds = int
Profiler = Callable[[Action, Milliseconds], None]


def print_profiling_info(action: Action, time_milliseconds: Milliseconds):
    """
        A simple profiler, that just prints out the profiling information on the console.

        Args:
            action (Action): the name of the action printed on the console, to fit the Profiler-protocol.
            time_milliseconds (Milliseconds): the time in milliseconds the action took. Argument to fit the Profiler-protocol.

        Returns: None

        Side Effects:
            Prints: "Profiling <action> took HHMMSSss."
    """
    print(f"Profiling: {action} took {format_ms_HHMMSSss(time_milliseconds)}")


def with_profile_printing(action: Action, wrapped_function: Callable[[...], T]) -> Callable[[...], T]:
    """
        Applies print_profiling_info (see there) to the callable as a profiler.

        Args:
            action (Action): the name of the action printed on the console.
            wrapped_function (Callable[[...], T]): the callable to profile.
    """
    return with_profiler(print_profiling_info, action, wrapped_function)


def with_profiler(profiler: Profiler, action: Action, wrapped_function: Callable[[...], T]) -> Callable[[...], T]:
    """
        Executes a function informing a profiler about the action and how long it took to do it.

        Args:
            profiler (Profiler): the profiler to be feed the profiling information into. May be None in which case no profiling is performed.
            action (Action): the name of the action executed. Will be given to the profiler.
            wrapped_function (Callable[[...], T]): the function to be profiled.
    """
    if not profiler:
        return wrapped_function

    def _wrapped(*args, **kwargs) -> T:
        with Stopwatch() as stopwatch:
            result = wrapped_function(*args, **kwargs)
        profiler(action, stopwatch.time_elapsed_millis)
        return result

    return _wrapped


@dataclass
class Profiling(ContextManager):
    """
        A context manager to profile an action with a given profiler.
        For example:
        ```
        with Profiling("My action"):
            do_something()
        ```
        will print:
        ```
        Profiling: My action took 00:00:00.123
        ```
        to the console.

        Args:
            action (Action): The name of the action to profile.
            profiler (Profiler): The profiler to use. Defaults to print_profiling_info.
    """
    action: Action
    profiler: Profiler = print_profiling_info
    _stop_watch: Optional[Stopwatch] = None

    def __enter__(self) -> "Profiling":
        self._stop_watch = Stopwatch()
        self._stop_watch.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_watch.stop()
        self.profiler(self.action, self._stop_watch.time_elapsed_millis)