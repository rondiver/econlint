"""Tests for ECON001: External calls in loops."""

from pathlib import Path

from econlint.parser import parse_file
from econlint.rules.econ001 import ECON001
from econlint.suppression import filter_suppressed

FIXTURES = Path(__file__).parent / "fixtures" / "econ001"


def run_rule(file_path: Path) -> tuple[list, dict]:
    """Run ECON001 on a file and return warnings and source cache."""
    result = parse_file(file_path)
    assert result is not None
    tree, source = result
    rule = ECON001(file_path, source)
    rule.visit(tree)
    source_cache = {file_path: source.splitlines()}
    return rule.warnings, source_cache


def test_positive_for_loop():
    """External call in for loop should trigger."""
    warnings, _ = run_rule(FIXTURES / "positive_for_loop.py")
    assert len(warnings) == 1
    assert warnings[0].code == "ECON001"
    assert "requests.get" in warnings[0].pattern


def test_positive_list_comp():
    """External call in list comprehension should trigger."""
    warnings, _ = run_rule(FIXTURES / "positive_list_comp.py")
    assert len(warnings) == 1
    assert warnings[0].code == "ECON001"
    assert "httpx.get" in warnings[0].pattern


def test_positive_while_loop():
    """External call in while loop should trigger."""
    warnings, _ = run_rule(FIXTURES / "positive_while_loop.py")
    assert len(warnings) >= 1
    assert warnings[0].code == "ECON001"


def test_negative_batched():
    """Batched call outside loop should not trigger."""
    warnings, _ = run_rule(FIXTURES / "negative_batched.py")
    assert len(warnings) == 0


def test_suppressed_ignore():
    """Suppressed warning should be filtered out."""
    warnings, source_cache = run_rule(FIXTURES / "suppressed_ignore.py")
    assert len(warnings) == 1
    filtered = filter_suppressed(warnings, source_cache)
    assert len(filtered) == 0
