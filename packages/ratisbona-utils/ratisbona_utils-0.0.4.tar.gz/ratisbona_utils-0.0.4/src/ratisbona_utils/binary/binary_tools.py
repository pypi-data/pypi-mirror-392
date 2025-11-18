from dataclasses import dataclass
from math import ceil, log2


def mask(num_bits: int) -> int:
    """
        Returns a mask with the lowest num_bits bits set to 1.

        Params:
            num_bits: The number of bits to set to 1.

        Returns:
            An integer with the lowest num_bits bits set to 1.
    """
    return (1 << num_bits) - 1


def bitsize(an_int: int) -> int:
    """
        Returns the number of bits needed to represent an integer.

        Params:
            an_int: The integer to determine the number of bits for.

        Returns:
            The number of bits needed to represent an integer.
    """
    return ceil(log2(an_int + 1))


@dataclass
class BitUnstuffer:
    """
        A class to retrieve single bits from a byte stream.
    """
    _contents: bytes
    _queue: int
    _bits_in_queue: int = 0

    def __init__(self, contents: bytes):
        self._contents = contents
        self._reload()

    def _reload(self):
        assert self._bits_in_queue == 0
        num_bytes = min(len(self._contents), 4)
        self._queue = int.from_bytes(self._contents[:num_bytes], 'big', signed=False)
        self._contents = self._contents[num_bytes:]
        self._bits_in_queue = 8 * num_bytes

    def _do_get_bits(self, num_bits) -> int:
        if num_bits == 0:
            return 0
        if num_bits > self._bits_in_queue:
            raise BufferError(f'{num_bits} bits requested but only {self._bits_in_queue} bits in queue anymore.')
        self._bits_in_queue -= num_bits
        retval = self._queue >> self._bits_in_queue & mask(num_bits)
        if self._bits_in_queue == 0:
            self._reload()
        return retval

    def has_more_bits(self):
        """
            Returns `True` if there are more bits to retrieve.

            Returns:
                `True` if there are more bits to retrieve, `False` otherwise.
        """
        return self._bits_in_queue > 0 # Remember that reload is triggered if queuelength 0 is reached.

    def get_bits(self, num_bits) -> int:
        """
            Retrieves the next `num_bits` bits from the byte stream.

            Params:
                num_bits: The number of bits to retrieve.

            Returns:
                The next `num_bits` bits from the byte stream.
        """
        assert num_bits <= 32
        num_bits_to_fetch = num_bits
        bits = 0
        if num_bits_to_fetch >= self._bits_in_queue:
            bits_fetched = self._bits_in_queue
            bits = self._do_get_bits(bits_fetched)
            num_bits_to_fetch -= bits_fetched
            bits <<= num_bits_to_fetch
        bits |= self._do_get_bits(num_bits_to_fetch)
        return bits


@dataclass
class BitStuffer:
    """
        A class to store single bits in a byte stream.
    """
    _auto_flush: bool

    _results: bytes = b''
    _queue: int = 0
    _capacity = 32

    def __init__(self, auto_flush=True):
        """
            Constructor.
        Args:
            auto_flush:  If `True` the stream is flushed before returning it.
        """
        self._auto_flush = auto_flush

    def _do_stuff_bits(self, bits: int, num_bits: int):
        assert num_bits <= self._capacity
        self._queue = self._queue << num_bits | bits & mask(num_bits)
        if num_bits == self._capacity:
            self._results += self._queue.to_bytes(4, 'big', signed=False)
            self._capacity = 32
            self._queue = 0
        else:
            self._capacity -= num_bits

    def flush(self):
        """
            Flushes the remaining bits to the byte stream, padding the stream with 0s if necessary.
        """
        if self._capacity == 32:
            return
        full_bytes_flushed = self._capacity // 8
        self._do_stuff_bits(0, self._capacity)
        self._results = bytes(self._results[:-full_bytes_flushed])

    def stuff_bits(self, bits: int, num_bits: int):
        """
            Stores the next `num_bits` bits in the byte stream.

            Params:
                bits: The bits to store.
                num_bits: The number of bits to store.
        """
        while num_bits > 0:
            num_bits_to_stuff = min(self._capacity, num_bits)
            the_bits_to_stuff = bits >> num_bits - num_bits_to_stuff
            self._do_stuff_bits(the_bits_to_stuff, num_bits_to_stuff)
            num_bits -= num_bits_to_stuff

    def to_bytes(self):
        """
            Returns the byte stream.
            if `auto_flush` is `True` the stream is flushed before returning.

        Returns:
            The byte stream.

        """
        if self._auto_flush:
            self.flush()
        return self._results

def to_int16(bindata: bytes) -> list[int]:
    """
        Converts a byte stream to a list of unsigned 16-bit integers, reading the bytes in little-endian order.

        Args:
            bindata: The byte stream to convert.

        Returns:
            A list of unsigned 16-bit integers.
    """
    as_bytearray = bytearray(bindata)
    while len(as_bytearray) % 2 != 0:
        as_bytearray.append(0)
    as_int16 = [
        int.from_bytes(as_bytearray[i : i + 2], byteorder="little")
        for i in range(0, len(as_bytearray), 2)
    ]
    return as_int16
