from __future__ import annotations

import sys
import traceback
from typing import TypeVar, Generic, Callable

T = TypeVar("T")
E = TypeVar("E", bound=Exception)
V = TypeVar("V")
U = TypeVar("U")


class UnexpectedNothingError(Exception):
    """
    This error is raised when a value was expected but nothing was encountered,
    for example by the "or_blow_up"-Method.

    Args:
        message (str): The error message.
        *args: The other arguments.

    Fields:
        message (str): The error message.
        traceback (str): The traceback of the error.
        *args: The other arguments
    """

    def __init__(self, *args):
        super().__init__(
            "Nothing was encountered where an value was expected in a Maybe", *args
        )


def key_error_to_nothing(error: Exception) -> Maybe[Exception | None]:
    """
    Converts a KeyError to a Nothing.

    Args:
        error (Exception): The error to convert.

    Returns:
        Maybe[Exception | None]: The converted error.
    """
    if isinstance(error, KeyError):
        return Nothing
    return error


class Maybe(Generic[T]):
    """
    This Maybe Monad can be used as a MaybeMonad or even as an ErrorMonad.

    If you wrap a value that is None, the Maybe will be a Nothing.
    If you wrap a value that inherits from Exception, the Maybe will be an Error.
    If you wrap another Maybe that Maybe will be unwrapped transparently. (If it's
    error or nothing this will be error or nothing, so there is not Just(Nothing) or Just(Error))
    If you finally wrap just an ordinary value then the Maybe will be a Just.
    """

    def __init__(self, value: T | None):
        # Maybes are transparently unwrapped.
        if value is not None and isinstance(value, Maybe):
            self._value = value._value
        else:
            self._value = value

    def __getitem__(self, item):
        """
        Allows to access the value of the monad directly.
        """
        if not self:
            return self

        if isinstance(item, Maybe):
            if not item:
                return item
            item = item._value

        if not hasattr(self._value, "__getitem__"):
            return Error(TypeError(f"{self._value} is not subscriptable"))

        if not item in self._value:
            return Nothing

        return Maybe(self._value[item])

    def __repr__(self):
        """
        Returns a string representation of the monad.
        """
        if self.is_just:
            return f"Just({self._value})"
        if self.is_error:
            return f"Error({self._value})"
        return "Nothing"

    def __add__(self, other):
        """
        Adds the value of the monad to another value.
        """

        if isinstance(other, str):
            return str(self) + other

        return NotImplemented

    def __radd__(self, other):
        """
        Adds the value of the monad to another value.
        """

        if isinstance(other, str):
            return other + str(self)

        return NotImplemented

    def __bool__(self):
        """
        Returns True if the Maybe is a Just.
        """
        return self.is_just

    def __eq__(self, other):
        """
        Compares the value of the monad with another value.

        Args:
            other: The other value to compare with.

        Returns:
            bool: True if the value of the monad is equal to the other value, False otherwise.
        """

        if not isinstance(other, Maybe):
            return self._value == other

        return self._value == other._value

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._value)

    def __iter__(self):
        """
        Returns an iterator over the value of the monad.
        """
        if not self:
            return iter([])

        if not hasattr(self._value, "__iter__"):
            return iter([self])

        return iter([Just(item) for item in self._value])

    def __in__(self, other):
        """
        Returns True if the value of the monad is in the other value.
        """
        if not self:
            return False

        return self._value in other

    def __contains__(self, item):
        """
        Returns True if the value of the monad contains the item.
        """
        if not self:
            return False

        if isinstance(item, Maybe):
            if not item:
                return False
            item = item._value

        return item in self._value or item == self._value

    @staticmethod
    def just(value: T | Maybe[T]) -> Maybe[T]:
        """
        Creates a Just, ensuring that is not Nothing or Error.
        """
        if value is None:
            raise ValueError(
                "None is not what I would call Just a value.\n"
                "I'm assuming you f-ed up, but if you really want a None-Value use the constant Nothing.\n"
                "Finally Maybe(...) will construct a Maybe from a value, if the value is None then\n"
                "Nothing is constructed.\n"
            )

        if isinstance(value, Exception):
            raise ValueError(
                "Well that is an Error and not just a value.\n"
                "I'm assuming you f-ed up, but if you really want an Exception-Value use Error(...) to construct an erorr.\n"
                "Finally Maybe(...) will construct a Maybe from a value, if the value is an Exception then\n"
                "Error is constructed.\n"
            )

        if isinstance(value, Maybe):
            if not value:
                raise ValueError(
                    "You may try to wrap a Just into a Just, in which case you'll end up with\n"
                    "just a Just.\n"
                    "But if you wrap a Nothing or an Error in a Just, I will refuse to do so,\n"
                    "assuming you f-ed up.\n"
                    "If you want to create a Maybe from a Maybe then use Maybe(...) instead,\n"
                    "which will also just return your Maybe.\n"
                )
        return Maybe(value)

    @staticmethod
    def error(value: E | Maybe[E]) -> Maybe[E]:
        """
        Creates an Error, ensuring that is not Nothing or Just.
        """
        if value is None:
            raise ValueError(
                "None is not what I would call an Error.\n"
                "I'm assuming you f-ed up, but if you really want a None-Value use the constant Nothing.\n"
                "Finally Maybe(...) will construct a Maybe from a value, if the value is None then\n"
                "Nothing is constructed.\n"
            )

        if isinstance(value, Maybe):
            if not value.is_error:
                raise ValueError(
                    "You may try to wrap an Error into an Error, in which case you'll end up with\n"
                    "just an Error.\n"
                    "But if you wrap a Nothing or a Just in an Error, I will refuse to do so,\n"
                    "assuming you f-ed up.\n"
                    "If you want to create a Maybe from a Maybe then use Maybe(...) instead,\n"
                    "which will also just return your Maybe.\n"
                )
            return Maybe(value.unwrap_error())

        if not isinstance(value, Exception):
            raise ValueError(
                "Well that is not an Error but a value.\n"
                "I'm assuming you f-ed up, but if you really want a value use Just(...) to construct a value.\n"
                "Finally Maybe(...) will construct a Maybe from a value, if the value is an Exception then\n"
                "Error is constructed.\n"
            )

        return Maybe(value)

    @staticmethod
    def with_errorhandling(
        a_function: Callable[[...], U] | Maybe[Callable[[...], U]], *args, **kwargs
    ) -> Maybe[V]:
        """
        Calls a function with monadic error handling.

        Args:
            a_function (Callable | Maybe[Callable]): The function to call. Will be passed the other arguments.
            The function is allowed to be a Maybe[Callable], in which case the function is unwrapped before calling.
            args (Any | Maybe[Any]): The other arguments to pass to the function
            kwargs (dict[str, Any | Maybe[Any]): The other keyword arguments to pass to the function

        Returns:
            Maybe[V]: The result of the function call, an error or nothing. Surely returns Nothing if function is a Nothing.
            If the function is an error, that error. If any of the arguments is a Nothing or a Maybe, that is returned.
            If the function returns an Error or Nothing, that is returned. If the function throws an error, that is returned.
            If the function returns just a value, than Just(value) is returned.
        """
        DEBUG=False

        if isinstance(a_function, Maybe):
            if not a_function:
                return a_function
            a_function = a_function._value

        unwrapped_args = []
        for arg in args:
            if isinstance(arg, Maybe):
                if not arg:
                    return arg
                arg = arg._value
            unwrapped_args.append(arg)

        unwrapped_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, Maybe):
                if not value:
                    return value
                value = value._value
            unwrapped_kwargs[key] = value

        try:
            if DEBUG:
                print(f"About to invoke {a_function.__name__}:")
                for arg in unwrapped_args:
                    print(f"  {arg} ({type(arg)})")
                for key, value in unwrapped_kwargs.items():
                    print(f"  {key}={value} ({type(value)})")

            return Maybe(  # Note: Function might return a Maybe, in which case it will be transparently unwrapped.
                a_function(*unwrapped_args, **unwrapped_kwargs)
            )
        except Exception as any_exception:
            any_exception.add_note(traceback.format_exc())
            if DEBUG:
                print("Caught an exception:", any_exception)
                sys.stdout.flush()
            return Maybe.error(any_exception)

    @property
    def is_just(self):
        """
        Returns True if the Maybe is a Just.
        """
        return self._value is not None and not isinstance(self._value, Exception)

    @property
    def is_error(self):
        """
        Returns True if the Maybe is an Error.
        """
        return isinstance(self._value, Exception)

    @property
    def is_nothing(self):
        """
        Returns True if the Maybe is a Nothing.
        """
        return self._value is None

    def bind(
        self, a_function: Callable[[...], V | Maybe[V]], *args, **kwargs
    ) -> Maybe[V]:
        """
        Binds a function to the ResultMonad. Function can throw exceptions which will
        be caught and returned as an error status in the ResultMonad, for convenience.

        Args:
            a_function (Callable | Maybe[Callable]):
            The function to bind to the result monad. Can be a Maybe[Callable] itself,
            in which case the function is unwrapped before calling.

            args: The other arguments to pass to the function. Maybes can be among them,
            in which case they will be unwrapped before passing.

            kwargs: The other keyword arguments to pass to the function, also maybe unwrapped.

        Returns:
            Maybe[V]: The result of the function call, an error or nothing. If this is nothing, surely nothing.
            If this is error, that error. If there's all right with this but someting fishy with a maybe function,
            that error. If there are errors or nothings in the args, that errors. Finally, if the function throws an
            error, then that error.
        """

        if not self:
            return self

        return Maybe.with_errorhandling(a_function, self, *args, **kwargs)

    def bind_or_bust(
        self, a_function: Callable[[...], V | Maybe[V]], *args, **kwargs
    ) -> V:
        """
        Binds a function to the ResultMonad. Function can throw exceptions which will
        be caught and returned as an error status in the ResultMonad, for convenience.

        Args:
            a_function (Callable | Maybe[Callable]):
            The function to bind to the result monad. Can be a Maybe[Callable] itself,
            in which case the function is unwrapped before calling.

            args: The other arguments to pass to the function. Maybes can be among them,
            in which case they will be unwrapped before passing.

            kwargs: The other keyword arguments to pass to the function, also maybe unwrapped.

        Returns:
            Maybe[V]: The result of the function call, an error or nothing. If this is nothing, surely nothing.
            If this is error, that error. If there's all right with this but someting fishy with a maybe function,
            that error. If there are errors or nothings in the args, that errors. Finally, if the function throws an
            error, then that error.
        """

        return self.bind(a_function, *args, **kwargs).maybe_raise_error()

    def maybe_recover(
        self,
        a_function: Callable[[E | None], T | Maybe[T]],
        *args,
        **kwargs,
    ) -> Maybe[T]:
        """
        Recover from an error or nothing status by applying a function to the Maybe.

        If all is well, function is not called.

        Args:y
            a_function: The function to apply to the error value. Will be passsed the error_value of the
            monad as the first argument or None, if the monad is a Nothing. The function can
            be a Maybe[Callable], in which case the function is unwrapped before calling.
            If the function is an error or a Nothing, the original Error will result.

            args: The other arguments to pass to the function. Will be passed after the error_value. If
            an arg is a Maybe, it will be unwrapped before passing. If an arg is an error or a Nothing,
            the original Error will result.
        """
        if self.is_just:
            return self

        maybe_better = Maybe.with_errorhandling(
            a_function, self._value, *args, **kwargs
        )

        if maybe_better.is_error:
            return self

        return maybe_better

    def maybe_warn(self, message: str | Callable[[T], None]) -> Maybe[T]:
        if not self.is_error:
            return self

        if isinstance(message, str):
            print(message, self._value)

        if isinstance(message, Callable):
            message(self._value)

        return self

    def __or__(self, other: Maybe[V]) -> Maybe[T | V]:
        """
        Return the value of the monad or the value of another monad if the monad is error.
        """
        if not self:
            return other
        return self

    def unwrap_value(self) -> T:
        """
        Get the value of the monad. If the monad is Nothing, None will be returned.

        Returns:
            The value of the monad.

        Raises:
            ValueError: If the monad is an error.
        """
        if self.is_error:
            raise ValueError("You must not unwrap a ResultMonad with an error status.")

        if self.is_nothing:
            raise ValueError("You must not unwrap a ResultMonad with a nothing status.")

        return self._value

    def unwrap_error(self) -> E:
        """
        Get the error value of the monad.

        Returns:
            The error value of the monad.

        Raises:
            ValueError: If the monad is not an error.
        """
        if not self.is_error:
            raise ValueError(
                "You must not unwrap the error of a ResultMonad that in fact is a success."
            )
        return self._value

    def maybe_raise_error(self):
        """
        Raises the error of the monad, if it is an Error.

        Returns:
            The monad, unchanged. Note that if it was an error, well, good luck obtaining the return value...
        """
        if self.is_error:
            raise self._value

        return self

    def value_or_throw(self):
        """
        Unwraps the value of the monad, if it is a Just.
        Raises the error of the monad, if it is an Error.
        Raises UnexpectedNothingError, if the monad is a Nothing.
        """
        self.maybe_raise_error()

        if self.is_nothing:
            unexpected_nothing_error = UnexpectedNothingError()
            unexpected_nothing_error.add_note(
                "Traceback:\n" + "".join(traceback.format_stack())
            )
            raise unexpected_nothing_error

        return self._value

    def default_or_throw(self, default: T) -> T:
        """
        Unwraps the value of the monad, if it is a Just.
        Raises the error of the monad, if it is an Error.
        Returns the default value, if the monad is a Nothing.
        """
        self.maybe_raise_error()

        if self.is_nothing:
            return default

        return self._value

    def default_or_error(self, default: T) -> Maybe[T]:
        if self.is_error:
            return self
        if self.is_nothing:
            return Just(default)
        return self

    def default_also_on_error(self, default: T) -> T:
        """
        Unwraps the value of the monad, if it is a Just.
        Raises the error of the monad, if it is an Error.
        Returns the default value, if the monad is a Nothing.
        """
        if not self:
            return default

        return self._value


with_errorhandling = Maybe.with_errorhandling
Just = Maybe.just
Error = Maybe.error
Nothing = Maybe(None)
