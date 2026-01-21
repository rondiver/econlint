"""Tests for ECON004: Unbounded fan-out."""

from pathlib import Path

from econlint.parser import parse_file
from econlint.rules.econ004 import ECON004
from econlint.suppression import filter_suppressed

FIXTURES = Path(__file__).parent / "fixtures" / "econ004"


def run_rule(file_path: Path) -> list:
    """Run ECON004 on a file and return warnings."""
    result = parse_file(file_path)
    assert result is not None
    tree, source = result
    rule = ECON004(file_path, source)
    rule.visit(tree)
    return rule.warnings


def test_positive_gather():
    """asyncio.gather without semaphore should trigger."""
    warnings = run_rule(FIXTURES / "positive_gather.py")
    assert len(warnings) == 1
    assert warnings[0].code == "ECON004"
    assert "gather" in warnings[0].pattern.lower()


def test_positive_executor():
    """ThreadPoolExecutor without max_workers should trigger."""
    warnings = run_rule(FIXTURES / "positive_executor.py")
    assert len(warnings) == 1
    assert warnings[0].code == "ECON004"
    assert "ThreadPoolExecutor" in warnings[0].pattern


def test_negative_bounded():
    """ThreadPoolExecutor with max_workers should not trigger."""
    warnings = run_rule(FIXTURES / "negative_bounded.py")
    assert len(warnings) == 0


def test_negative_semaphore():
    """asyncio.gather with semaphore should not trigger."""
    warnings = run_rule(FIXTURES / "negative_semaphore.py")
    assert len(warnings) == 0


def test_suppressed_ignore():
    """Suppressed warning should be filtered out."""
    warnings = run_rule(FIXTURES / "suppressed_ignore.py")
    assert len(warnings) == 1
    filtered = filter_suppressed(warnings)
    assert len(filtered) == 0
