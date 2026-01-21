"""Base rule class for econlint."""

import ast
from pathlib import Path

from econlint.warnings import Warning, EXPLANATIONS


class BaseRule(ast.NodeVisitor):
    """Base class for all econlint rules.

    Subclasses should:
    - Set `code` class attribute (e.g., "ECON001")
    - Set `message` class attribute (e.g., "External call inside loop")
    - Override visit methods to detect patterns
    - Call `self.add_warning()` when a pattern is found
    """

    code: str = ""
    message: str = ""

    def __init__(self, file_path: Path, source: str) -> None:
        self.file_path = file_path
        self.source = source
        self.source_lines = source.splitlines()
        self.warnings: list[Warning] = []

    def add_warning(self, node: ast.AST, pattern: str) -> None:
        """Add a warning for the given AST node."""
        warning = Warning(
            code=self.code,
            message=self.message,
            file=self.file_path,
            line=node.lineno,
            pattern=pattern,
            explanation=EXPLANATIONS.get(self.code, ""),
        )
        self.warnings.append(warning)

    def get_call_name(self, node: ast.Call) -> str:
        """Extract a readable name from a Call node."""
        return self._get_expr_name(node.func)

    def _get_expr_name(self, node: ast.expr) -> str:
        """Recursively build a dotted name from an expression."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_expr_name(node.value)
            if value_name:
                return f"{value_name}.{node.attr}"
            return node.attr
        elif isinstance(node, ast.Call):
            return self._get_expr_name(node.func) + "()"
        elif isinstance(node, ast.Subscript):
            return self._get_expr_name(node.value) + "[]"
        return ""

    def has_keyword(self, node: ast.Call, keyword: str) -> bool:
        """Check if a Call node has a specific keyword argument."""
        return any(kw.arg == keyword for kw in node.keywords)
