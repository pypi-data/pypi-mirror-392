from typing import Iterable, Callable

from ratisbona_utils.io import FileIterable


class collect:

    def __init__(self, collection_generator: Callable):
        self.collection_generator = collection_generator

    def __ror__(self, other):
        return self.collection_generator(other)


class cat(Iterable):
    def __init__(self, iterable: Iterable):
        self.iterable = iterable

    def __or__(self, other):
        if isinstance(other, Callable):
            return cat(map(other, self.iterable))

        return NotImplemented

    def __iter__(self):
        return iter(self.iterable)

class fcat(cat):
    def __init__(self, file_path):
        super().__init__(FileIterable(file_path))








