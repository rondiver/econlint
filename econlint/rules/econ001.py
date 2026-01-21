"""ECON001: External calls in loops."""

import ast
import re

from econlint.rules.base import BaseRule


# HTTP methods that are actually network calls (not list methods like append)
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "request"}

# Explicit external call prefixes (known HTTP/API libraries)
HTTP_LIBRARY_PREFIXES = (
    "httpx.", "aiohttp.", "urllib.request.", "http.client.",
    "urllib3.", "asks.", "treq.", "grequests.",
)

# Explicit external call methods (full match)
EXTERNAL_METHODS = {
    # Database
    "cursor.execute", "cursor.executemany", "cursor.fetchone", "cursor.fetchall",
    "cursor.fetchmany", "connection.execute", "session.execute", "session.query",
    # AWS boto3 common operations
    "s3.get_object", "s3.put_object", "s3.delete_object",
    "dynamodb.get_item", "dynamodb.put_item", "dynamodb.query",
    "sqs.send_message", "sqs.receive_message",
    "sns.publish",
}

# Patterns for receivers that suggest external API clients
# More conservative than before - requires suffix pattern
EXTERNAL_RECEIVER_SUFFIXES = re.compile(
    r"(_client|_api|_service|_connection|_session|Client|Api|Service)$"
)

# Methods that are typically external API calls when on a client-like receiver
API_METHODS = {
    "get", "post", "put", "patch", "delete", "head", "options",  # HTTP verbs
    "request", "send", "fetch", "call", "invoke", "execute",  # Generic API methods
    "query", "read", "write", "create", "update", "remove",  # CRUD operations
}


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

        # Check HTTP library prefixes
        for prefix in HTTP_LIBRARY_PREFIXES:
            if call_name.startswith(prefix):
                return True, call_name

        # Special handling for 'requests' library (could conflict with list variable named 'requests')
        if call_name.startswith("requests."):
            method = call_name.split(".")[-1].lower()
            if method in HTTP_METHODS:
                return True, call_name

        # Check explicit external methods
        for method in EXTERNAL_METHODS:
            if call_name.endswith(method):
                return True, call_name

        # Check for client-like receivers with API methods
        parts = call_name.rsplit(".", 1)
        if len(parts) == 2:
            receiver, method = parts
            # Check if receiver looks like an API client
            if EXTERNAL_RECEIVER_SUFFIXES.search(receiver):
                # Any method call on a *_client, *_api, etc. is suspicious
                return True, call_name
            # Check if it's an API method on something that might be a client
            if method.lower() in API_METHODS:
                # Only flag if the receiver name suggests it's a client
                if EXTERNAL_RECEIVER_SUFFIXES.search(receiver):
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
