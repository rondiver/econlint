"""Text output formatter for econlint."""

from econlint.warnings import Warning


def format_text(warnings: list[Warning]) -> str:
    """Format warnings as human-readable text.

    Output format:
    ECON001: External call inside loop at app/sync.py:45

      Pattern: requests.get() called inside for loop

      Economic risk: Each loop iteration incurs API/network cost.
      ...
    """
    if not warnings:
        return ""

    parts: list[str] = []

    for warning in warnings:
        header = f"{warning.code}: {warning.message} at {warning.file}:{warning.line}"

        explanation_lines = warning.explanation.strip().split("\n")
        indented_explanation = "\n".join(f"  {line}" for line in explanation_lines)

        block = f"""{header}

  Pattern: {warning.pattern}

{indented_explanation}
"""
        parts.append(block)

    return "\n".join(parts)
