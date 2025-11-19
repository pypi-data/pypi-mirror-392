import pytest
from pytoon import loads, ToonDecodeError


def test_decode_primitive_array_inline():
    text = "tags[3]: red,green,blue"
    data = loads(text)
    assert data == ["red", "green", "blue"] or data == {"tags": ["red", "green", "blue"]}


def test_decode_primitive_array_block():
    text = """
    nums[3]:
      1
      2
      3
    """
    data = loads(text)
    assert data == {"nums": [1, 2, 3]}


def test_decode_tabular_array():
    text = """
    users[2]{id,name}:
      1,Alice
      2,Bob
    """
    data = loads(text)
    assert data == {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }


def test_decode_tabular_array_inline_rows():
    text = "pairs[2]{a,b}: 1,x,2,y"
    data = loads(text)
    assert data == {
        "pairs": [
            {"a": 1, "b": "x"},
            {"a": 2, "b": "y"},
        ]
    }


def test_decode_array_length_mismatch():
    text = """
    nums[2]:
      1
      2
      3
    """
    with pytest.raises(ToonDecodeError):
        loads(text)
