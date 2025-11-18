from typing import Iterable


class FileIterable(Iterable[str]):
    def __init__(self, file_path):
        self.file_path = file_path

    def __iter__(self):
        with open(self.file_path) as filehandle:
            for line in filehandle:
                yield line.rstrip('\n')
