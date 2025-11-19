"""
PyTOON: lightweight TOON (Token-Oriented Object Notation) support for Python.

Public API is intentionally similar to PyYAML:
- load / loads
- dump / dumps
- to_json / from_json
"""

from __future__ import annotations

from typing import IO, Any

from .decoder import loads as _loads_impl
from .encoder import dumps as _dumps_impl
from .errors import ToonDecodeError, ToonEncodeError

__all__ = [
    "load",
    "loads",
    "dump",
    "dumps",
    "to_json",
    "from_json",
    "ToonDecodeError",
    "ToonEncodeError",
    "__version__",
]

__version__ = "0.1.0"


def loads(text: str) -> Any:
    """
    Parse a TOON string and return the corresponding Python object.

    :raises ToonDecodeError: if the input is not valid TOON according to PyTOON's parser.
    """
    return _loads_impl(text)


def load(stream: IO[str]) -> Any:
    """
    Parse TOON content from a text file-like object.

    :param stream: A readable text stream (e.g. result of open(..., 'r')).
    """
    return loads(stream.read())


def dumps(obj: Any, *, indent: int = 2) -> str:
    """
    Serialize a Python object to a TOON string.

    :param indent: Number of spaces per indentation level (default: 2).
    :raises ToonEncodeError: if the object contains structures
                             not supported by the encoder.
    """
    return _dumps_impl(obj, indent=indent)


def dump(obj: Any, stream: IO[str], *, indent: int = 2) -> None:
    """
    Serialize a Python object as TOON and write it to a file-like object.

    :param stream: A writable text stream (e.g. result of open(..., 'w')).
    """
    stream.write(dumps(obj, indent=indent))


# --- JSON helpers -----------------------------------------------------------

import json as _json  # noqa: E402  (import after type hints for simplicity)


def to_json(obj: Any, **json_kwargs: Any) -> str:
    """
    Convenience function: serialize a Python object to a JSON string.

    This is just a light wrapper around json.dumps, so you can stay within
    the pytoon namespace in your code.
    """
    return _json.dumps(obj, **json_kwargs)


def from_json(json_str: str) -> Any:
    """
    Convenience function: parse a JSON string into Python objects.

    This is just a thin wrapper around json.loads.
    """
    return _json.loads(json_str)
