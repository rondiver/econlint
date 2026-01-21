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


def get_suppressed_codes(source_lines: list[str], line: int) -> set[str] | None:
    """Get suppressed codes for a specific line.

    Args:
        source_lines: List of source code lines
        line: 1-indexed line number

    Returns:
        None if no suppression comment found
        Empty set if all codes are suppressed (bare ignore)
        Set of specific codes if ignore=CODE1,CODE2
    """
    if line < 1 or line > len(source_lines):
        return None

    source_line = source_lines[line - 1]
    match = IGNORE_PATTERN.search(source_line)

    if not match:
        return None

    codes_str = match.group(1)
    if codes_str is None:
        return set()

    return set(code.strip() for code in codes_str.split(","))


def is_suppressed(warning: Warning, source_cache: dict[Path, list[str]]) -> bool:
    """Check if a warning is suppressed by an inline comment.

    Args:
        warning: The warning to check
        source_cache: Dict mapping file paths to their source lines
    """
    source_lines = source_cache.get(warning.file)
    if source_lines is None:
        return False

    suppressed = get_suppressed_codes(source_lines, warning.line)

    if suppressed is None:
        return False

    if len(suppressed) == 0:
        return True

    return warning.code in suppressed


def filter_suppressed(
    warnings: list[Warning],
    source_cache: dict[Path, list[str]]
) -> list[Warning]:
    """Filter out suppressed warnings.

    Args:
        warnings: List of warnings to filter
        source_cache: Dict mapping file paths to their source lines
    """
    return [w for w in warnings if not is_suppressed(w, source_cache)]
