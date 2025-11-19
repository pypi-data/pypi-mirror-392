from pytoon.scalars import parse_scalar, format_scalar


def test_scalar_null():
    assert parse_scalar("null") is None
    assert format_scalar(None) == "null"


def test_scalar_bool():
    assert parse_scalar("true") is True
    assert parse_scalar("false") is False
    assert format_scalar(True) == "true"
    assert format_scalar(False) == "false"


def test_scalar_int():
    assert parse_scalar("10") == 10
    assert format_scalar(42) == "42"


def test_scalar_float():
    assert parse_scalar("3.14") == 3.14
    assert format_scalar(2.5) == "2.5"


def test_scalar_string_bare():
    assert parse_scalar("hello") == "hello"
    assert format_scalar("hello") == "hello"


def test_scalar_string_json_quoted():
    assert parse_scalar('"hi there"') == "hi there"
