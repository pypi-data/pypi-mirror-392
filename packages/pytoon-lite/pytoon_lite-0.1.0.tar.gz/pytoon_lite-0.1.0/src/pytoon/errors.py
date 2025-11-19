from __future__ import annotations


class ToonError(Exception):
    """Base class for all PyTOON-related exceptions."""


class ToonDecodeError(ToonError):
    """Raised when TOON input cannot be parsed into a Python object."""


class ToonEncodeError(ToonError):
    """Raised when a Python object cannot be serialized as TOON."""
