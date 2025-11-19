import pytest
from pytoon import dumps, ToonEncodeError


def test_encode_primitive_array_inline():
    obj = {"tags": ["a", "b", "c"]}
    out = dumps(obj)
    lines = out.strip().splitlines()
    assert lines[0].startswith("tags[3]:")
    assert "a,b,c" in lines[0]


def test_encode_primitive_array_indented():
    # Encoder always uses inline representation for primitives,
    # so this is a consistency check only.
    out = dumps(["x", "y"])
    assert out.startswith("[2]:")
    assert "x,y" in out


def test_encode_tabular_array():
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }
    out = dumps(data)
    lines = out.splitlines()
    assert lines[0].startswith("users[2]{id,name}:")
    assert "1,Alice" in out
    assert "2,Bob" in out


def test_encode_array_of_mixed_invalid():
    with pytest.raises(ToonEncodeError):
        dumps(["a", {"x": 1}])  # mixed primitive and object not allowed
