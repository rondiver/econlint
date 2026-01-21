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
    parser.add_argument(
        "--disable",
        type=str,
        default="",
        help="Disable specific rules (comma-separated, e.g., --disable=ECON001,ECON003)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude paths matching pattern (can be used multiple times)",
    )
    return parser.parse_args(argv)


def get_enabled_rules(disabled: str) -> list:
    """Get list of enabled rule classes based on disabled rules."""
    if not disabled:
        return ALL_RULES

    disabled_codes = {code.strip().upper() for code in disabled.split(",")}
    return [rule for rule in ALL_RULES if rule.code not in disabled_codes]


def run_analysis(
    path: Path,
    rules: list,
    exclude_patterns: list[str]
) -> tuple[list[Warning], dict[Path, list[str]]]:
    """Run all rules on all discovered files.

    Returns:
        Tuple of (warnings, source_cache)
    """
    warnings: list[Warning] = []
    source_cache: dict[Path, list[str]] = {}

    for file_path in discover_files(path, exclude_patterns):
        result = parse_file(file_path)
        if result is None:
            continue

        tree, source = result
        source_cache[file_path] = source.splitlines()

        for rule_class in rules:
            rule = rule_class(file_path, source)
            rule.visit(tree)
            warnings.extend(rule.warnings)

    return warnings, source_cache


def main(argv: list[str] | None = None) -> int:
    """Main entry point for econlint CLI."""
    args = parse_args(argv)

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 2

    try:
        rules = get_enabled_rules(args.disable)
        warnings, source_cache = run_analysis(args.path, rules, args.exclude)
        warnings = filter_suppressed(warnings, source_cache)
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
