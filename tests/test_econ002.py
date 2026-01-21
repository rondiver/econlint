"""Tests for ECON002: Unbounded retries."""

from pathlib import Path

from econlint.parser import parse_file
from econlint.rules.econ002 import ECON002
from econlint.suppression import filter_suppressed

FIXTURES = Path(__file__).parent / "fixtures" / "econ002"


def run_rule(file_path: Path) -> tuple[list, dict]:
    """Run ECON002 on a file and return warnings and source cache."""
    result = parse_file(file_path)
    assert result is not None
    tree, source = result
    rule = ECON002(file_path, source)
    rule.visit(tree)
    source_cache = {file_path: source.splitlines()}
    return rule.warnings, source_cache


def test_positive_tenacity():
    """Tenacity retry without stop should trigger."""
    warnings, _ = run_rule(FIXTURES / "positive_tenacity.py")
    assert len(warnings) == 1
    assert warnings[0].code == "ECON002"
    assert "retry" in warnings[0].pattern.lower()


def test_positive_while_true():
    """While True retry loop without counter should trigger."""
    warnings, _ = run_rule(FIXTURES / "positive_while_true.py")
    assert len(warnings) == 1
    assert warnings[0].code == "ECON002"


def test_negative_bounded():
    """Retry with stop parameter should not trigger."""
    warnings, _ = run_rule(FIXTURES / "negative_bounded.py")
    assert len(warnings) == 0


def test_suppressed_ignore():
    """Suppressed warning should be filtered out."""
    warnings, source_cache = run_rule(FIXTURES / "suppressed_ignore.py")
    assert len(warnings) == 1
    filtered = filter_suppressed(warnings, source_cache)
    assert len(filtered) == 0
