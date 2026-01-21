"""File discovery for econlint."""

from collections.abc import Iterator
from pathlib import Path


def discover_files(path: Path) -> Iterator[Path]:
    """Discover Python files to analyze.

    If path is a file, yield it if it's a .py file.
    If path is a directory, recursively yield all .py files.
    """
    if path.is_file():
        if path.suffix == ".py":
            yield path
    elif path.is_dir():
        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                yield file_path
