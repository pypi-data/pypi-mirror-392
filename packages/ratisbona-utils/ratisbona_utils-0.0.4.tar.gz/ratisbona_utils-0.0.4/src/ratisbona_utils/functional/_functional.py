from collections import defaultdict
from itertools import tee
from typing import Iterable, TypeVar, Callable, Any, Union

from ratisbona_utils.monads import Maybe

# Payload-Type
T = TypeVar("T")

# Key-Type
KT = TypeVar("KT")

# Result-Type
RT = TypeVar("RT")

# Id-Type
IDT = TypeVar("IDT")

# Typealias for an id-index, mapping from id to the object of that id.
IdIndex = dict[IDT, T]

Provider = Callable[[], T]
Consumer = Callable[[T], None]
Predicate = Callable[[T], bool]
Function = Callable[[T], RT]

def ensure_collection(value: Any) -> Union[list, set, tuple]:
    """
    Ensure that the value is a list. If it is not, return an empty list.

    Args:
        value: The value to check.

    Returns:
        A list containing the value if it is a list, or an empty list otherwise.
    """
    if isinstance(value, (list, set, tuple)):
        return value
    return [value]

def first(iterable: Iterable[T]) -> Maybe[T]:
    """
    Returns first element of an iterable or None, if the iterable did not provide any elements.

    Args:
        iterable: Any iterable. Not None.

        Returns:
            first element returned by iterable or Nothing, if iterable was empty.
    """
    return Maybe(next(iter(iterable), None))


def pairwise(iterable):
    """
    The "rough equivalence" of pairwise from python 3.9 is used here
    see https://docs.python.org/3/library/itertools.html#itertools.pairwise
    for original documentation

    Args:
        iterable: Any iterable. Not None.

    Returns:
        a generator that yields tuples of the form (iterable[i], iterable[i+1])
        for i in range(len(iterable) - 1)
    """

    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def identity(an_object: T) -> T:
    """
    Useful in cases where simply saying "identity" is clearer
    and more explicit than for example "lambda x: x"

    Args:
        an_object: any object.

    Return:
        the very same object.
    """
    return an_object  # coding this is the hell of a job, isn't it?


def create_id_index(
    iterable: Iterable[T], id_extractor: Callable[[T], IDT]
) -> IdIndex[IDT, T]:
    """
    The create_id_index function takes an iterable and a
    function that extracts an id from the elements of the iterable.
    It returns a dictionary that maps the extracted ids to the elements of the iterable.

    Args:
        iterable: Iterable[T]: The iterable to create an id-index for
        id_extractor: Callable[[T], IDT]: The function to extract
        an id from an element of the iterable

    Returns:
        A dictionary that maps the extracted ids to the elements of the iterable.
    """
    return dict((id_extractor(item), item) for item in iterable)


def nonunique_id_index(
    iterable: Iterable[T], id_extractor: Callable[[T], IDT]
) -> dict[IDT, list[T]]:
    """
    The nonunique_id_index function takes an iterable and a
    function that extracts an id from the elements of the iterable.
    It returns a dictionary that maps the extracted ids to a
    list of elements of the iterable that share the same id.

    Args:
        iterable: Iterable[T]: The iterable to create an id-index for
        id_extractor: Callable[[T], IDT]: The function to extract
        an id from an element of the iterable

    Returns:
        A dictionary that maps the extracted ids to a
        list of elements of the iterable that share the same id.
    """
    result: dict[IDT, list[T]] = defaultdict(list)
    for item in iterable:
        result[id_extractor(item)].append(item)
    return result


def substitute_for_none(
    substitute: RT, input_function: Callable[[T], RT]
) -> Callable[[T], RT]:
    def _wrapped(input_value: T) -> RT:
        if input_value is None:
            return substitute
        result = input_function(input_value)
        if result is None:
            return substitute
        return result

    return _wrapped


def nth_element(n: int) -> Callable[[tuple[T, ...]], T]:
    """
    Conveniently creates a callable that, as soon as
     given a tuple as input, selects the n-th element as output.
    Intended use is in situations, where for example
    a key-function needs to be provided, that simply selects one of
    the elements out of a tuple. That way you don't
     have to write "key=lambda x: x[n]" each time, but you can simply go
    key=nth_element(n)

    Args:
        n: number of the element that the callable is to return

    Returns:
        Callable, it accepts a tuple and returns the n-th element of the tuple.
    """
    return lambda a_tuple: a_tuple[n]


def map_all_values_of_the_dictionary(
    mapping_function: Callable[[T], RT], the_dict: dict[KT, T]
) -> dict[KT, RT]:
    """
    Helper function to apply a mapping function to all values of a dictionary.

    Args:
        mapping_function:   The function to apply to each value in the dictionary
        the_dict:   The dictionary containing the values that should be mapped by the mapping function.

    Returns:
        a new dictionary with the same keys as the one supplied, but each value is mapped by the mapping function.
    """
    return dict((k, mapping_function(v)) for k, v in the_dict.items())


def nonordered_groupby(
    iterable: Iterable[T],
    key: Callable[[T], KT],
    value: Callable[[T], RT] = lambda x: x,
) -> dict[KT, list[T]]:
    """
    The nonordered_groupby function takes an iterable, a key function and an optional value function.
    The key-function is used to derive a key from every item in the iterable.
    The value-function is used to derive a value from every item in the iterable.
    A map is created that maps each key to a list of values that have the key in common.

    In contrast to iterators.groupby, the nonordered_groupby
    function does not require the iterable to be sorted.

    Args:
        iterable: Iterable[T]: The iterable to group
        key: Callable[[T], KT]: The key function
        value: Callable[[T], RT]: The value function. Defaults to identity.

        T: TypeVar for contents of the iterable
        KT: TypeVar for the Key-Type extracted by the key function.
        RT: TypeVar for the Result-Type extracted by the value-function.

    Returns:
        Dictionary that maps keys to list of values.
    """
    result: dict[KT, list[T]] = defaultdict(list)
    for item in iterable:
        result[key(item)].append(value(item))
    return result


def repeat_function(function: Callable, times: int, *args):
    """
    Repeats a function call with the result of the previous call as arguments for the next call.

    Args:
        function: The function to repeat.
        times: The number of times to repeat the function.
        *args: The arguments to pass to the function.

    Returns:
        The result of the last function call.

    """
    if times < 0:
        raise ValueError(f"Requested to repeat {times} times. Impossible.")
    targs = args
    for _ in range(0, times):
        targs = function(*targs)
        if not isinstance(targs, tuple) and not isinstance(targs, list):
            targs = (targs,)
    return targs


def negate(function: callable) -> callable:
    """
    Returns a function that negates the result of the given function.
    """
    return lambda *args, **kwargs: -function(*args, **kwargs)

def ensure_iterator(*args):
    """
    Returns an iterator over the given arguments.
    """
    for arg in args:
        if isinstance(arg, Iterable) and not isinstance(arg, str):
            yield from arg
            continue
        yield arg
