"""Tests for ECON003: N+1 query patterns."""

from pathlib import Path

from econlint.parser import parse_file
from econlint.rules.econ003 import ECON003
from econlint.suppression import filter_suppressed

FIXTURES = Path(__file__).parent / "fixtures" / "econ003"


def run_rule(file_path: Path) -> tuple[list, dict]:
    """Run ECON003 on a file and return warnings and source cache."""
    result = parse_file(file_path)
    assert result is not None
    tree, source = result
    rule = ECON003(file_path, source)
    rule.visit(tree)
    source_cache = {file_path: source.splitlines()}
    return rule.warnings, source_cache


def test_positive_for_get():
    """N+1 pattern with get() in for loop should trigger."""
    warnings, _ = run_rule(FIXTURES / "positive_for_get.py")
    assert len(warnings) == 1
    assert warnings[0].code == "ECON003"
    assert "get_user" in warnings[0].pattern


def test_positive_list_comp():
    """N+1 pattern in list comprehension should trigger."""
    warnings, _ = run_rule(FIXTURES / "positive_list_comp.py")
    assert len(warnings) == 1
    assert warnings[0].code == "ECON003"
    assert "fetch_profile" in warnings[0].pattern


def test_negative_batch():
    """Batch fetch should not trigger."""
    warnings, _ = run_rule(FIXTURES / "negative_batch.py")
    assert len(warnings) == 0


def test_suppressed_ignore():
    """Suppressed warning should be filtered out."""
    warnings, source_cache = run_rule(FIXTURES / "suppressed_ignore.py")
    assert len(warnings) == 1
    filtered = filter_suppressed(warnings, source_cache)
    assert len(filtered) == 0
