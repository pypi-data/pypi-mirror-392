from typing import List, Callable, Any



def nullsafe_decorator(
    exclude_indices: List[int] = [], exclude_keys: List[str] = []
) -> Callable[[Callable[[...], Any]], Callable[[...], Any]]:
    """
    Decorator to make a function nullsafe.

    Args:
        exclude_indices:
            List of indices to exclude from the nullsafe check. If an argument at that index is None,
            the function will still be called.
        exclude_keys:
            List of keys to exclude from the nullsafe check. If a keyword argument with that
            key is None, the function will still be called.
    """

    def decorator(function: Callable[[...], Any]) -> Callable[[...], Any]:
        def wrapper(*args, **kwargs):
            for idx, arg in enumerate(args):
                if arg is None and idx not in exclude_indices:
                    return None
            for key, value in kwargs.items():
                if value is None and key not in exclude_keys:
                    return None
            return function(*args, **kwargs)

        return wrapper

    return decorator


def nullsafe(
    function: Callable[[...], Any],
    exclude_indices: List[int] = [],
    exclude_keys: List[str] = [],
) -> Callable[[...], Any]:
    """
    Make a function nullsafe. Convenience function for nullsafe_decorator.

    Args:
        function:
            The function to make nullsafe.
        exclude_indices:
            List of indices to exclude from the nullsafe check. If an argument at that index is None,
            the function will still be called.
        exclude_keys:
            List of keys to exclude from the nullsafe check. If a keyword argument with that
            key is None, the function will still be called.
    """
    return nullsafe_decorator(exclude_indices, exclude_keys)(function)


def saveget(dictionary, key, default=None):
    if not dictionary:
        return default
    return dictionary.get(key, default)


def substitute(value, substitute):
    return value if value else substitute


def has_keyvalue(dictionary, key):
    return dictionary.get(key, None) is not None