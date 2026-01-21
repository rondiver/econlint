"""Rule implementations for econlint."""

from econlint.rules.base import BaseRule
from econlint.rules.econ001 import ECON001
from econlint.rules.econ002 import ECON002
from econlint.rules.econ003 import ECON003
from econlint.rules.econ004 import ECON004

ALL_RULES: list[type[BaseRule]] = [ECON001, ECON002, ECON003, ECON004]

__all__ = ["BaseRule", "ECON001", "ECON002", "ECON003", "ECON004", "ALL_RULES"]
