"""ECON003: N+1 query patterns."""

import ast
import re

from econlint.rules.base import BaseRule


# Method names that suggest data fetching
FETCH_METHODS = re.compile(
    r"^(get|fetch|load|query|find|select|read|retrieve|lookup)(_|$)",
    re.IGNORECASE
)


class ECON003(BaseRule):
    """Detect N+1 query patterns."""

    code = "ECON003"
    message = "N+1 query pattern"

    def __init__(self, file_path, source):
        super().__init__(file_path, source)
        self.loop_vars: list[set[str]] = []

    def visit_For(self, node: ast.For) -> None:
        """Track for loop variables and check for N+1 patterns."""
        loop_vars = self._extract_loop_vars(node.target)
        self.loop_vars.append(loop_vars)
        self.generic_visit(node)
        self.loop_vars.pop()

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Check list comprehensions for N+1 patterns."""
        all_vars: set[str] = set()
        for generator in node.generators:
            all_vars.update(self._extract_loop_vars(generator.target))

        self.loop_vars.append(all_vars)
        self.generic_visit(node)
        self.loop_vars.pop()

    def visit_Call(self, node: ast.Call) -> None:
        """Check if a fetch-like call uses loop variables."""
        if self.loop_vars:
            call_name = self.get_call_name(node)
            method_name = call_name.split(".")[-1] if call_name else ""

            if FETCH_METHODS.match(method_name):
                if self._uses_loop_var(node):
                    self.add_warning(
                        node,
                        f"{call_name}() called with loop variable (N+1 pattern)"
                    )

        self.generic_visit(node)

    def _extract_loop_vars(self, target: ast.expr) -> set[str]:
        """Extract variable names from a loop target."""
        names: set[str] = set()

        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                names.update(self._extract_loop_vars(elt))

        return names

    def _uses_loop_var(self, node: ast.Call) -> bool:
        """Check if any argument to the call uses a loop variable."""
        current_vars = set().union(*self.loop_vars) if self.loop_vars else set()

        for arg in node.args:
            if self._expr_uses_vars(arg, current_vars):
                return True

        for kw in node.keywords:
            if self._expr_uses_vars(kw.value, current_vars):
                return True

        return False

    def _expr_uses_vars(self, node: ast.expr, var_names: set[str]) -> bool:
        """Check if an expression uses any of the given variable names."""
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id in var_names:
                return True
        return False
