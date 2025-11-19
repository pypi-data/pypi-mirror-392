from pytoon import loads


def test_decode_simple_object():
    text = """
    name: Alice
    age: 30
    """
    data = loads(text)
    assert data == {"name": "Alice", "age": 30}


def test_decode_nested_object():
    text = """
    config:
      version: 1
      nested:
        enabled: true
    """
    data = loads(text)
    assert data["config"]["nested"]["enabled"] is True


def test_decode_scalar_top_level():
    assert loads("42") == 42
    assert loads("true") is True
    assert loads("hello") == "hello"
