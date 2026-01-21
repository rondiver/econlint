"""ECON002: Unbounded retries."""

import ast

from econlint.rules.base import BaseRule


class ECON002(BaseRule):
    """Detect unbounded retry patterns."""

    code = "ECON002"
    message = "Unbounded retry pattern"

    def __init__(self, file_path, source):
        super().__init__(file_path, source)
        self._in_while_true = False
        self._while_true_node = None

    def visit_Call(self, node: ast.Call) -> None:
        """Check for tenacity/retrying decorators without limits."""
        call_name = self.get_call_name(node)

        # Check tenacity @retry without stop=
        if call_name in ("retry", "tenacity.retry"):
            if not self.has_keyword(node, "stop"):
                self.add_warning(node, f"{call_name}() without stop= parameter")

        # Check retrying @retry without stop_max_attempt_number
        if call_name in ("retrying.retry", "Retrying"):
            if not self.has_keyword(node, "stop_max_attempt_number"):
                self.add_warning(
                    node, f"{call_name}() without stop_max_attempt_number"
                )

        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Check for while True with try/except and sleep (manual retry loop)."""
        if self._is_while_true(node):
            if self._has_try_except_sleep(node):
                if not self._has_counter_check(node):
                    self.add_warning(
                        node, "while True retry loop without attempt limit"
                    )

        self.generic_visit(node)

    def _is_while_true(self, node: ast.While) -> bool:
        """Check if this is a while True loop."""
        if isinstance(node.test, ast.Constant):
            return node.test.value is True
        if isinstance(node.test, ast.NameConstant):
            return node.test.value is True
        return False

    def _has_try_except_sleep(self, node: ast.While) -> bool:
        """Check if the while loop contains try/except with sleep."""
        has_try = False
        has_sleep = False

        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                has_try = True
            if isinstance(child, ast.Call):
                call_name = self.get_call_name(child)
                if "sleep" in call_name:
                    has_sleep = True

        return has_try and has_sleep

    def _has_counter_check(self, node: ast.While) -> bool:
        """Check if there's a counter/attempt tracking mechanism."""
        source_segment = ast.get_source_segment(self.source, node) or ""
        lower_source = source_segment.lower()

        counter_patterns = [
            "attempt", "retry", "tries", "count", "max_",
            "limit", "< ", "<= ", "> ", ">= "
        ]
        return any(pattern in lower_source for pattern in counter_patterns)
