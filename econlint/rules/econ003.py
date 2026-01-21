"""ECON003: N+1 query patterns."""

import ast
import re

from econlint.rules.base import BaseRule


# Method names that suggest data fetching from external sources
FETCH_METHODS = re.compile(
    r"^(get|fetch|load|query|find|select|read|retrieve|lookup)(_|[A-Z]|$)",
    re.IGNORECASE
)

# Patterns that indicate the receiver is likely an external API
EXTERNAL_RECEIVER_PATTERNS = re.compile(
    r"(_api|_client|_service|_repository|_repo|_dao|_store|_backend|_remote|_db|_database|"
    r"Api$|Client$|Service$|Repository$|Repo$|Dao$|Store$|Backend$|Remote$|Database$)",
    re.IGNORECASE
)

# Safe receivers - known stdlib modules and local data patterns
SAFE_RECEIVERS = {
    # Stdlib modules
    "json", "pickle", "marshal", "csv", "xml", "html", "re", "os", "sys",
    "pathlib", "collections", "itertools", "functools", "operator",
    # Built-in types
    "dict", "list", "set", "tuple", "str", "bytes", "frozenset",
    # Common config/settings patterns
    "settings", "config", "options", "opts", "attrs", "params", "kwargs",
    "environ", "env", "os.environ", "metadata", "headers", "cookies",
    # Common local variable patterns
    "self", "cls", "item", "obj", "data", "result", "response", "request",
    "cache", "mapping", "lookup", "index", "registry", "values", "stats",
    # Regex/pattern matching
    "pattern", "regex", "match", "matcher",
    # Test-related
    "run", "runner", "spider", "crawler", "spider_loader", "downloader",
}

# Safe method suffixes - these are typically local accessors, not external calls
SAFE_METHOD_SUFFIXES = {
    "path", "priority", "list", "value", "key", "name", "type", "attr",
    "slot", "item", "iter", "match",
}


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
                    if self._is_likely_external_call(call_name, method_name):
                        self.add_warning(
                            node,
                            f"{call_name}() called with loop variable (N+1 pattern)"
                        )

        self.generic_visit(node)

    def _is_likely_external_call(self, call_name: str, method_name: str) -> bool:
        """Check if this call is likely an external API call."""
        parts = call_name.rsplit(".", 1)

        # Bare function call (no receiver)
        if len(parts) < 2:
            # Only flag if it looks like an API function
            return EXTERNAL_RECEIVER_PATTERNS.search(call_name) is not None

        receiver = parts[0]

        # Check if method name ends with safe suffix (getpath, getlist, etc.)
        method_lower = method_name.lower()
        for suffix in SAFE_METHOD_SUFFIXES:
            if method_lower.endswith(suffix):
                return False

        # Check if receiver is in safe list
        receiver_base = receiver.split(".")[-1].lower()
        if receiver_base in SAFE_RECEIVERS:
            return False

        # Check full receiver path for safe patterns
        receiver_lower = receiver.lower()
        for safe in SAFE_RECEIVERS:
            if safe in receiver_lower:
                return False

        # Check if receiver looks like an external API
        if EXTERNAL_RECEIVER_PATTERNS.search(receiver):
            return True

        # Default: only flag if it really looks like an API
        # Be conservative - don't flag unless we're confident
        return False

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
