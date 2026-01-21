"""Command-line interface and orchestration for econlint."""

import argparse
import sys
from pathlib import Path

from econlint.discovery import discover_files
from econlint.parser import parse_file
from econlint.rules import ALL_RULES
from econlint.suppression import filter_suppressed
from econlint.formatters import format_text, format_json
from econlint.warnings import Warning


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="econlint",
        description="Detect expensive code patterns in Python files.",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to file or directory to analyze",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    return parser.parse_args(argv)


def run_analysis(path: Path) -> list[Warning]:
    """Run all rules on all discovered files."""
    warnings: list[Warning] = []

    for file_path in discover_files(path):
        result = parse_file(file_path)
        if result is None:
            continue

        tree, source = result

        for rule_class in ALL_RULES:
            rule = rule_class(file_path, source)
            rule.visit(tree)
            warnings.extend(rule.warnings)

    return warnings


def main(argv: list[str] | None = None) -> int:
    """Main entry point for econlint CLI."""
    args = parse_args(argv)

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 2

    try:
        warnings = run_analysis(args.path)
        warnings = filter_suppressed(warnings)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.json_output:
        output = format_json(warnings)
    else:
        output = format_text(warnings)

    if output:
        print(output)

    return 1 if warnings else 0
