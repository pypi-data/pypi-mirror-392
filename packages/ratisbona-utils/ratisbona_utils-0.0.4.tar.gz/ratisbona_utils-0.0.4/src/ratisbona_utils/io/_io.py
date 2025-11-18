import os
import shutil
import sys
from importlib import resources
from importlib.abc import Traversable
from pathlib import Path

UTF8 = {"encoding": "utf-8"}


def errprint(*args, **kwargs):
    """
    Prints to stderr.

    Args:
        *args: Arguments to print.
        **kwargs: Keyword arguments to print.

    Returns:
        None

    Side Effects:
        - Prints to stderr.
    """
    print(*args, file=sys.stderr, **kwargs)


def maybe_backup_file(filepath: Path) -> bool:
    if not filepath.exists():
        return False
    print(f"Backuping {filepath}")
    with filepath.with_suffix(".bak").open("wb") as backup, filepath.open("rb") as file:
        backup.write(file.read())
    return True


def get_config_dir(toolname="ratisbona_utils", ensure=True, ensure_ratisbona=True):
    """
    Returns the configuration directory for a tool.

    Args:
        toolname (str): The name of the tool. Default: 'ratisbona_utils'.
        ensure (bool): If True, create the configuration directory if it does not exist.

    Returns:
        Path of the configuration directory.

    Side Effects:
        - Maybe creates the configuration directory, if it does not exist.
    """
    if ensure_ratisbona and not toolname.lower().startswith("ratisbona_"):
        toolname = f"ratisbona_{toolname}"

    config_dir = Path(os.path.expanduser(f"~/.local/share/{toolname}"))
    if ensure:
        config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_resource(package: str, resource_name: str) -> Traversable:
    """
    Returns a stream to read a resource file from a package.

    Args:
        package (str): The package containing the resource (e.g., 'my_package.resources').
        resource_name (str): The name of the resource file (e.g., 'example.txt').

    Returns:
        A file-like object to read the resource content.

    Side Effects:
        - None

    """
    return resources.files(package).joinpath(resource_name)

def copy_resource_file(
    package: str, resource_name: str, output_filename: Path, chunk_size: int = 4096
):
    """
    Reads a resource file from a package and copies it chunkwise to an output file.

    Args:

        package (str): The package containing the resource (e.g., 'my_package.resources').
        resource_name (str): The name of the resource file (e.g., 'example.txt').
        output_file (Path): The destination file to which the content will be written.
        chunk_size: The size of chunks to copy at a time (default: 4096 bytes).

    Returns:
        None

    Side Effects:
        - Copies the resource file to the output file.

    """
    with (
        resources.files(package).joinpath(resource_name).open("rb") as src,
        open(output_filename, "wb") as dst,
    ):
        shutil.copyfileobj(src, dst, length=chunk_size)
