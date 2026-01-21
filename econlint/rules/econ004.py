"""ECON004: Unbounded fan-out."""

import ast
import re

from econlint.rules.base import BaseRule

# Pattern to detect Semaphore instantiation in code
SEMAPHORE_PATTERN = re.compile(r"\bSemaphore\s*\(")


class ECON004(BaseRule):
    """Detect unbounded concurrent fan-out patterns."""

    code = "ECON004"
    message = "Unbounded fan-out"

    def __init__(self, file_path, source):
        super().__init__(file_path, source)
        self._has_semaphore = self._check_for_semaphore()

    def _check_for_semaphore(self) -> bool:
        """Check if the module uses a Semaphore."""
        for line in self.source_lines:
            # Skip comment-only lines
            code_part = line.split("#")[0]
            if SEMAPHORE_PATTERN.search(code_part):
                return True
        return False

    def visit_Call(self, node: ast.Call) -> None:
        """Check for unbounded fan-out patterns."""
        call_name = self.get_call_name(node)

        # asyncio.gather with spread operator
        if call_name in ("asyncio.gather", "gather"):
            if self._has_starred_arg(node) and not self._has_semaphore:
                self.add_warning(
                    node,
                    "asyncio.gather(*...) without Semaphore"
                )

        # ThreadPoolExecutor without max_workers
        if call_name in ("ThreadPoolExecutor", "concurrent.futures.ThreadPoolExecutor"):
            if not self.has_keyword(node, "max_workers"):
                self.add_warning(
                    node,
                    "ThreadPoolExecutor() without max_workers"
                )

        # ProcessPoolExecutor without max_workers
        if call_name in ("ProcessPoolExecutor", "concurrent.futures.ProcessPoolExecutor"):
            if not self.has_keyword(node, "max_workers"):
                self.add_warning(
                    node,
                    "ProcessPoolExecutor() without max_workers"
                )

        # multiprocessing.Pool without processes limit
        if call_name in ("Pool", "multiprocessing.Pool"):
            if not node.args and not self.has_keyword(node, "processes"):
                self.add_warning(
                    node,
                    "multiprocessing.Pool() without processes limit"
                )

        self.generic_visit(node)

    def _has_starred_arg(self, node: ast.Call) -> bool:
        """Check if a call has a starred argument (*args)."""
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                return True
        return False
