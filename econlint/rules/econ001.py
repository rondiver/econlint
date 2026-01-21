"""ECON001: External calls in loops."""

import ast
import re

from econlint.rules.base import BaseRule


# Patterns that indicate external calls
HTTP_PREFIXES = ("requests.", "httpx.", "aiohttp.", "urllib.request.")
DB_PATTERNS = ("cursor.execute", "session.execute", "connection.execute")
GENERIC_PATTERNS = re.compile(r"(client|api|service|connection)", re.IGNORECASE)


class ECON001(BaseRule):
    """Detect external calls inside loops."""

    code = "ECON001"
    message = "External call inside loop"

    def __init__(self, file_path, source):
        super().__init__(file_path, source)
        self.loop_depth = 0

    def _is_external_call(self, node: ast.Call) -> tuple[bool, str]:
        """Check if a Call node represents an external call.

        Returns (is_external, call_name).
        """
        call_name = self.get_call_name(node)
        if not call_name:
            return False, ""

        # HTTP libraries
        for prefix in HTTP_PREFIXES:
            if call_name.startswith(prefix):
                return True, call_name

        # Database patterns
        for pattern in DB_PATTERNS:
            if pattern in call_name:
                return True, call_name

        # Generic patterns (client, api, service, connection)
        if GENERIC_PATTERNS.search(call_name):
            return True, call_name

        return False, call_name

    def _check_call(self, node: ast.Call) -> None:
        """Check a call node if we're inside a loop."""
        if self.loop_depth > 0:
            is_external, call_name = self._is_external_call(node)
            if is_external:
                self.add_warning(node, f"{call_name}() called inside loop")

    def visit_For(self, node: ast.For) -> None:
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        self._check_call(node)
        self.generic_visit(node)
