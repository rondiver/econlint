"""JSON output formatter for econlint."""

import json

from econlint.warnings import Warning


def format_json(warnings: list[Warning]) -> str:
    """Format warnings as JSON."""
    data = [
        {
            "code": w.code,
            "message": w.message,
            "file": str(w.file),
            "line": w.line,
            "pattern": w.pattern,
            "explanation": w.explanation,
        }
        for w in warnings
    ]
    return json.dumps(data, indent=2)
