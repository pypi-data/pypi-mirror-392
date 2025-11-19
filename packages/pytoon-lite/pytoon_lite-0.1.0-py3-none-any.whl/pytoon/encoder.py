from __future__ import annotations

import csv
import io
from collections.abc import Mapping, Sequence
from typing import Any, List, Tuple

from pytoon.errors import ToonEncodeError
from pytoon.scalars import format_scalar


def dumps(obj: Any, *, indent: int = 2) -> str:
    """
    Encode a Python object into TOON.

    Supported:
    - dict (possibly nested)
    - list/tuple of primitives
    - list/tuple of uniform dicts (tabular arrays)
    """
    if indent <= 0:
        raise ValueError("indent must be > 0")

    ctx = _EncodeContext(indent=indent)
    lines = ctx.encode_top(obj)
    return "\n".join(lines) + ("\n" if lines else "")


class _EncodeContext:
    def __init__(self, indent: int) -> None:
        self.indent_str = " " * indent

    # --- Public entry point for top-level -----------------------------------

    def encode_top(self, obj: Any) -> List[str]:
        # Top level: if it's a mapping, encode as object;
        # otherwise treat it like a bare value (array or scalar).
        if isinstance(obj, Mapping):
            lines: List[str] = []
            for key, value in obj.items():
                self._encode_key_value(lines, key, value, level=0)
            return lines

        # For bare values, we synthesize a pseudo-header.
        out: List[str] = []
        self._encode_value(out, obj, level=0, key=None)
        return out

    # --- Core dispatch ------------------------------------------------------

    def _encode_key_value(self, lines: List[str], key: Any, value: Any, *, level: int) -> None:
        if not isinstance(key, str):
            raise ToonEncodeError(f"TOON object keys must be strings, got {type(key)!r}")

        # Sequence?
        if self._is_sequence(value):
            self._encode_sequence(lines, value, level=level, key=key)
            return

        # Mapping?
        if isinstance(value, Mapping):
            indent = self.indent_str * level
            lines.append(f"{indent}{key}:")
            self._encode_mapping(lines, value, level=level + 1)
            return

        # Scalar
        scalar = format_scalar(value)
        indent = self.indent_str * level
        lines.append(f"{indent}{key}: {scalar}")

    def _encode_value(self, lines: List[str], value: Any, *, level: int, key: str | None) -> None:
        if isinstance(value, Mapping):
            if key is not None:
                indent = self.indent_str * level
                lines.append(f"{indent}{key}:")
                self._encode_mapping(lines, value, level=level + 1)
            else:
                self._encode_mapping(lines, value, level=level)
            return

        if self._is_sequence(value):
            self._encode_sequence(lines, value, level=level, key=key)
            return

        # Bare scalar at top-level
        scalar = format_scalar(value)
        indent = self.indent_str * level
        if key is not None:
            lines.append(f"{indent}{key}: {scalar}")
        else:
            lines.append(f"{indent}{scalar}")

    def _encode_mapping(self, lines: List[str], obj: Mapping[str, Any], *, level: int) -> None:
        for key, value in obj.items():
            self._encode_key_value(lines, key, value, level=level)

    # --- Sequences ----------------------------------------------------------

    @staticmethod
    def _is_sequence(value: Any) -> bool:
        return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))

    def _encode_sequence(
        self,
        lines: List[str],
        seq: Sequence[Any],
        *,
        level: int,
        key: str | None,
    ) -> None:
        n = len(seq)
        indent = self.indent_str * level

        if n == 0:
            header = f"{indent}{key}[0]:" if key is not None else f"{indent}[0]:"
            lines.append(header)
            return

        # Check if we have an array of uniform dicts (tabular array)
        is_uniform_dicts, field_names = self._inspect_uniform_dicts(seq)

        if is_uniform_dicts and field_names:
            header = self._header_for_array(n, key, field_names, indent)
            lines.append(header)
            for item in seq:
                assert isinstance(item, Mapping)
                row_values = [format_scalar(item.get(field)) for field in field_names]
                row_text = self._csv_row(row_values)
                row_indent = indent + self.indent_str
                lines.append(f"{row_indent}{row_text}")
            return

        # Otherwise, expect an array of primitives
        if not all(self._is_primitive(x) for x in seq):
            raise ToonEncodeError(
                "Only arrays of primitives or uniform dicts are supported by PyTOON. "
                "Got a sequence with mixed or nested values."
            )

        scalar_values = [format_scalar(x) for x in seq]
        csv_values = self._csv_row(scalar_values)
        header = self._header_for_array(n, key, None, indent)
        lines.append(f"{header} {csv_values}")

    @staticmethod
    def _is_primitive(value: Any) -> bool:
        from numbers import Number

        return value is None or isinstance(value, (bool, str, Number))

    @staticmethod
    def _inspect_uniform_dicts(seq: Sequence[Any]) -> Tuple[bool, Tuple[str, ...]]:
        """
        Check whether seq is a non-empty sequence of dicts with the same key set.

        Returns (is_uniform, field_names).
        """
        first = seq[0]
        if not isinstance(first, Mapping):
            return False, ()

        base_keys = list(first.keys())
        base_key_set = set(base_keys)

        if not base_keys:
            return False, ()

        for item in seq[1:]:
            if not isinstance(item, Mapping):
                return False, ()
            if set(item.keys()) != base_key_set:
                return False, ()

        return True, tuple(base_keys)

    @staticmethod
    def _csv_row(values: list[str]) -> str:
        """
        Join values into a CSV row using Python's csv writer, so quoting is correct
        when values contain commas, quotes, etc.
        """
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="")
        writer.writerow(values)
        return buf.getvalue()

    @staticmethod
    def _header_for_array(
        length: int,
        key: str | None,
        fields: Tuple[str, ...] | None,
        indent: str,
    ) -> str:
        if fields:
            fields_text = ",".join(fields)
            if key is None:
                return f"{indent}[{length}]{{{fields_text}}}:"
            return f"{indent}{key}[{length}]{{{fields_text}}}:"
        else:
            if key is None:
                return f"{indent}[{length}]:"
            return f"{indent}{key}[{length}]:"
