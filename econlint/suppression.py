"""Suppression handling for econlint.

Supports inline ignore comments:
  # econlint: ignore
  # econlint: ignore=ECON001
  # econlint: ignore=ECON001,ECON003
"""

import re
from pathlib import Path

from econlint.warnings import Warning


IGNORE_PATTERN = re.compile(
    r"#\s*econlint:\s*ignore(?:=([A-Z0-9,]+))?\s*$"
)


def get_suppressed_codes(file_path: Path, line: int) -> set[str] | None:
    """Get suppressed codes for a specific line.

    Returns:
        None if no suppression comment found
        Empty set if all codes are suppressed (bare ignore)
        Set of specific codes if ignore=CODE1,CODE2
    """
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    lines = source.splitlines()
    if line < 1 or line > len(lines):
        return None

    source_line = lines[line - 1]
    match = IGNORE_PATTERN.search(source_line)

    if not match:
        return None

    codes_str = match.group(1)
    if codes_str is None:
        return set()

    return set(code.strip() for code in codes_str.split(","))


def is_suppressed(warning: Warning) -> bool:
    """Check if a warning is suppressed by an inline comment."""
    suppressed = get_suppressed_codes(warning.file, warning.line)

    if suppressed is None:
        return False

    if len(suppressed) == 0:
        return True

    return warning.code in suppressed


def filter_suppressed(warnings: list[Warning]) -> list[Warning]:
    """Filter out suppressed warnings."""
    return [w for w in warnings if not is_suppressed(w)]
