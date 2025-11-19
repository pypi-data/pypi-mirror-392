from __future__ import annotations

from typing import Any


def format_scalar(value: Any) -> str:
    """
    Convert a Python scalar into its TOON textual representation.

    The encoder aims to stay close to JSON scalar representations:
    - bool -> "true"/"false"
    - None -> "null"
    - numbers -> unchanged
    - strings -> bare when safe, JSON-quoted when necessary
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # String representation is mostly handled by CSV writer in encoder;
        # for single scalars we keep it as-is, quoting handled by caller if needed.
        return value

    raise TypeError(f"Unsupported scalar type for TOON: {type(value)!r}")


def parse_scalar(token: str) -> Any:
    """
    Parse a single scalar token into a Python value.

    Recognizes:
    - "null" -> None
    - "true"/"false" -> bool
    - int / float
    - JSON-style quoted strings
    - otherwise returns raw string
    """
    token = token.strip()
    if token == "":
        return ""

    # JSON-style string
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        import json

        return json.loads(token)

    lower = token.lower()
    if lower == "null":
        return None
    if lower == "true":
        return True
    if lower == "false":
        return False

    # Try integer
    try:
        return int(token)
    except ValueError:
        pass

    # Try float
    try:
        return float(token)
    except ValueError:
        pass

    # Fallback to string
    return token
