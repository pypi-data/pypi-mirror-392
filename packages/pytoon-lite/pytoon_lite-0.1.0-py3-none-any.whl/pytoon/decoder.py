from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from typing import Any, List, Tuple

from pytoon.errors import ToonDecodeError
from pytoon.scalars import parse_scalar


_INDENT_WIDTH_DEFAULT = 2


@dataclass
class _Line:
    indent: int
    text: str
    raw: str
    lineno: int


def loads(text: str) -> Any:
    """
    Parse a TOON string into a Python object.

    Parsing is indentation-based and supports:
    - nested objects
    - arrays of primitives (key[n]: ...)
    - tabular arrays of uniform objects (key[n]{a,b}: ...)
    """
    lines = _preprocess(text)
    if not lines:
        return None

    # Detect indent width from first indented line, otherwise default.
    indent_width = _detect_indent_width(lines) or _INDENT_WIDTH_DEFAULT

    # --- TOP-LEVEL ARRAY HANDLING ---
    # Case 1: Bare top-level array: "[3]:" with no key.
    # Case 2: Keyed top-level array: "nums[3]:"
    first = lines[0]
    key, length, fields, rest = _split_header(first.text)

    is_array = length is not None or fields is not None

    if is_array:
        value, next_index = _parse_array_block(lines, 0, indent_width, key=key)
        if next_index != len(lines):
            raise ToonDecodeError("Extra content after top-level array")

        # Case A: Bare array: return directly
        if key is None:
            return value

        # Case B: Keyed array: wrap into an object
        return {key: value}

    if len(lines) == 1 and not _is_array_header(first.text) and ":" not in first.text:
        return parse_scalar(first.text)

    obj, next_index = _parse_object_block(lines, 0, indent_width, expected_indent=0)
    if next_index != len(lines):
        raise ToonDecodeError("Extra content after top-level object")
    return obj


# --- Preprocessing ----------------------------------------------------------


def _preprocess(text: str) -> List[_Line]:
    raw_lines = text.splitlines()

    buf: List[Tuple[int, str, int]] = []
    for lineno, raw in enumerate(raw_lines, start=1):
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        buf.append((indent, raw.rstrip("\n\r"), lineno))

    if not buf:
        return []

    min_indent = min(indent for indent, _, _ in buf)

    out: List[_Line] = []
    for indent, raw, lineno in buf:
        norm_indent = indent - min_indent
        text_line = raw[min_indent:].lstrip()
        out.append(_Line(indent=norm_indent, text=text_line, raw=raw, lineno=lineno))

    return out


def _detect_indent_width(lines: List[_Line]) -> int | None:
    for line in lines:
        if line.indent > 0:
            return line.indent
    return None


# --- Parsing helpers --------------------------------------------------------


def _ensure_indent(line: _Line, expected: int) -> None:
    if line.indent != expected:
        raise ToonDecodeError(
            f"Unexpected indentation at line {line.lineno}: got {line.indent}, expected {expected}"
        )


def _split_header(
    text: str,
) -> Tuple[str | None, int | None, Tuple[str, ...] | None, str]:
    """
    Parse a header of the form:

      key[n]{a,b}: rest
      key[n]: rest
      [n]{a,b}: rest
      [n]: rest

    Returns (key, length, fields, rest).
    """
    # Find ':'
    if ":" not in text:
        return None, None, None, text
    head, rest = text.split(":", 1)
    rest = rest.lstrip()

    key: str | None
    length: int | None = None
    fields: Tuple[str, ...] | None = None

    # key + array length or bare array length
    if "[" in head and "]" in head:
        if head.startswith("["):
            key = None
            inside = head[1 : head.index("]")]
        else:
            key_part, after_key = head.split("[", 1)
            key = key_part.strip()
            inside = after_key.split("]", 1)[0]
        try:
            length = int(inside)
        except ValueError as exc:
            raise ToonDecodeError(f"Invalid array length in header: {head!r}") from exc

        # Optional fields part
        brace_start = head.find("{")
        if brace_start != -1:
            brace_end = head.rfind("}")
            if brace_end == -1 or brace_end < brace_start:
                raise ToonDecodeError(f"Malformed field list in header: {head!r}")
            fields_text = head[brace_start + 1 : brace_end].strip()
            if fields_text:
                fields = tuple(f.strip() for f in fields_text.split(",") if f.strip())
    else:
        # plain key:
        key = head.strip()

    return key, length, fields, rest


def _is_array_header(text: str) -> bool:
    key, length, fields, _ = _split_header(text)
    return length is not None or (key is None and fields is not None)


def _parse_csv_row(row: str) -> List[str]:
    buf = StringIO(row)
    reader = csv.reader(buf)
    for values in reader:
        return values
    return []


# --- Object block -----------------------------------------------------------


def _parse_object_block(
    lines: List[_Line],
    index: int,
    indent_width: int,
    expected_indent: int,
) -> Tuple[dict[str, Any], int]:
    """
    Parse an object starting at lines[index] with the given expected indentation.

    Returns (object, next_index).
    """
    result: dict[str, Any] = {}

    while index < len(lines):
        line = lines[index]
        if line.indent < expected_indent:
            break  # caller will handle
        if line.indent > expected_indent:
            raise ToonDecodeError(
                f"Unexpected extra indentation at line {line.lineno}: {line.raw!r}"
            )

        key, length, fields, rest = _split_header(line.text)

        # Array under key
        if length is not None or fields is not None:
            value, index = _parse_array_block(lines, index, indent_width, key)
            if key is None:
                raise ToonDecodeError(
                    f"Top-level array header not expected inside object at line {line.lineno}"
                )
            result[key] = value
            continue

        # Plain "key: value" or "key:" object
        if key is None:
            raise ToonDecodeError(f"Expected key at line {line.lineno}: {line.raw!r}")

        if rest != "":
            # Scalar value on the same line
            result[key] = parse_scalar(rest)
            index += 1
            continue

        # Nested object block
        index += 1
        child_indent = expected_indent + indent_width
        if index >= len(lines) or lines[index].indent < child_indent:
            # Empty object
            result[key] = {}
            continue

        child_obj, index = _parse_object_or_array(
            lines, index, indent_width, expected_indent=child_indent
        )
        result[key] = child_obj

    return result, index


def _parse_object_or_array(
    lines: List[_Line],
    index: int,
    indent_width: int,
    expected_indent: int,
) -> Tuple[Any, int]:
    """
    At this point, lines[index] is a non-blank line with indentation >= expected_indent.
    We decide whether it's an array header or nested object key.
    """
    line = lines[index]
    if line.indent != expected_indent:
        raise ToonDecodeError(
            f"Unexpected indentation at line {line.lineno}: got {line.indent}, "
            f"expected {expected_indent}"
        )

    if _is_array_header(line.text):
        # Array assigned to an implicit (already-known) key or bare array.
        value, next_index = _parse_array_block(lines, index, indent_width, key=None)
        return value, next_index

    # Otherwise, nested object
    return _parse_object_block(lines, index, indent_width, expected_indent)


# --- Array block ------------------------------------------------------------


def _parse_array_block(
    lines: List[_Line],
    index: int,
    indent_width: int,
    key: str | None,
) -> Tuple[Any, int]:
    """
    Parse an array whose header is at lines[index].

    Header may be:
      key[n]{a,b}: rest
      key[n]: rest
      [n]{a,b}: rest
      [n]: rest
    """
    header_line = lines[index]
    header_indent = header_line.indent
    _ensure_indent(header_line, header_indent)

    h_key, length, fields, rest = _split_header(header_line.text)

    # If key param was provided, it must match.
    if key is not None and h_key is not None and key != h_key:
        raise ToonDecodeError(
            f"Inconsistent key in array header at line {header_line.lineno}: "
            f"{h_key!r} (expected {key!r})"
        )

    key = key or h_key  # use header key if we didn't have one

    if length is None and fields is None:
        raise ToonDecodeError(
            f"Array header is missing length or fields at line {header_line.lineno}: "
            f"{header_line.raw!r}"
        )

    index += 1
    element_indent = header_indent + indent_width

    # Tabular array of objects
    if fields is not None:
        field_list = list(fields)
        rows: List[List[str]] = []

        # Inline row(s) in header, e.g. key[2]{a,b}:1,Alice,2,Bob
        if rest:
            tokens = _parse_csv_row(rest)
            if tokens:
                if len(tokens) % len(field_list) != 0:
                    raise ToonDecodeError(
                        f"Inline tabular row count not divisible by field count at line "
                        f"{header_line.lineno}"
                    )
                for i in range(0, len(tokens), len(field_list)):
                    rows.append(tokens[i : i + len(field_list)])

        # Indented rows
        while index < len(lines):
            line = lines[index]
            if line.indent < element_indent:
                break
            if line.indent > element_indent:
                raise ToonDecodeError(
                    f"Unexpected indentation in array row at line {line.lineno}: {line.raw!r}"
                )

            row_tokens = _parse_csv_row(line.text)
            rows.append(row_tokens)
            index += 1

        result: List[dict[str, Any]] = []
        for row in rows:
            if len(row) != len(field_list):
                raise ToonDecodeError(
                    f"Row length {len(row)} does not match fields length {len(field_list)} "
                    f"in tabular array, header line {header_line.lineno}"
                )
            obj = {field: parse_scalar(value) for field, value in zip(field_list, row)}
            result.append(obj)

        if length is not None and len(result) != length:
            raise ToonDecodeError(
                f"Declared length {length} does not match actual row count {len(result)} "
                f"in tabular array, header line {header_line.lineno}"
            )

        return result, index

    # Otherwise: array of primitives
    values: List[Any] = []
    if rest:
        tokens = _parse_csv_row(rest)
        values.extend(parse_scalar(tok) for tok in tokens)

    # Indented scalars (one per line, or CSV per line)
    while index < len(lines):
        line = lines[index]
        if line.indent < element_indent:
            break
        if line.indent > element_indent:
            raise ToonDecodeError(
                f"Unexpected indentation in primitive array at line {line.lineno}: {line.raw!r}"
            )
        tokens = _parse_csv_row(line.text)
        if tokens:
            values.extend(parse_scalar(tok) for tok in tokens)
        index += 1

    if length is not None and len(values) != length:
        raise ToonDecodeError(
            f"Declared length {length} does not match actual element count {len(values)} "
            f"in primitive array, header line {header_line.lineno}"
        )

    return values, index
