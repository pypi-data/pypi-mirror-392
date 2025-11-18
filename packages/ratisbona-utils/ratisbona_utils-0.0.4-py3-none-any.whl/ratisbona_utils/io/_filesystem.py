from pathlib import Path
from typing import Callable, Optional, TypeAlias

SizeNumBytes = int

# Typaliasen für die Callbacks
OnStart: TypeAlias = Callable[[Path, SizeNumBytes], None]  # file, size in bytes
OnProgress: TypeAlias = Callable[[Path, SizeNumBytes], None]  # file, bytes_transferred (delta)
OnFinish: TypeAlias = Callable[[Path, bool, Optional[Exception]], None]  # file, success, message
OnSkip: TypeAlias = Callable[[Path, str], None]  # file, reason


def copy_file(
    src: Path,
    dst: Path,
    on_start: Optional[OnStart] = None,
    on_progress: Optional[OnProgress] = None,
    on_finish: Optional[OnFinish] = None,
    chunk_size: int = 1024 * 1024,
):
    try:
        size = src.stat().st_size
        if on_start:
            on_start(src, size)

        transferred = 0
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while chunk := fsrc.read(chunk_size):
                fdst.write(chunk)
                transferred += len(chunk)
                if on_progress:
                    on_progress(src, len(chunk))

        if on_finish:
            on_finish(src, True, None)

    except Exception as e:
        if on_finish:
            on_finish(src, False, e)
        raise e
