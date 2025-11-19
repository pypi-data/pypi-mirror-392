from pytoon import dumps


def test_encode_simple_object():
    obj = {"name": "Alice", "age": 30}
    out = dumps(obj)
    assert "name: Alice" in out
    assert "age: 30" in out


def test_encode_nested_object():
    obj = {"context": {"location": "Mars", "mission": "exploration"}}
    out = dumps(obj)
    assert "context:" in out
    assert "  location: Mars" in out
    assert "  mission: exploration" in out


def test_encode_scalar_top_level():
    assert dumps(123).strip() == "123"
    assert dumps("xyz").strip() == "xyz"
