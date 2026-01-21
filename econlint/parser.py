"""AST parsing for econlint."""

import ast
import sys
from pathlib import Path


def parse_file(file_path: Path) -> tuple[ast.Module, str] | None:
    """Parse a Python file into an AST.

    Returns the AST and source code, or None if parsing fails.
    Errors are printed to stderr.
    """
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        return None

    return tree, source
