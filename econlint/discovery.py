"""File discovery for econlint."""

import fnmatch
from collections.abc import Iterator
from pathlib import Path


def discover_files(
    path: Path,
    exclude_patterns: list[str] | None = None
) -> Iterator[Path]:
    """Discover Python files to analyze.

    Args:
        path: File or directory to analyze
        exclude_patterns: Glob patterns to exclude (e.g., ["**/tests/**", "**/venv/**"])

    If path is a file, yield it if it's a .py file.
    If path is a directory, recursively yield all .py files.
    """
    exclude_patterns = exclude_patterns or []

    def is_excluded(file_path: Path) -> bool:
        """Check if a path matches any exclusion pattern."""
        path_str = str(file_path)
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # Also check just the relative path parts
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
            # Check if any parent directory matches
            for part in file_path.parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
        return False

    if path.is_file():
        if path.suffix == ".py" and not is_excluded(path):
            yield path
    elif path.is_dir():
        for file_path in path.rglob("*.py"):
            if file_path.is_file() and not is_excluded(file_path):
                yield file_path
