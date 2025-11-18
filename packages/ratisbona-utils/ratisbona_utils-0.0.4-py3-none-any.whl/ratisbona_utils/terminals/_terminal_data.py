import shutil


def get_terminal_width(default=80):
    try:
        return shutil.get_terminal_size().columns
    except OSError:
        return default