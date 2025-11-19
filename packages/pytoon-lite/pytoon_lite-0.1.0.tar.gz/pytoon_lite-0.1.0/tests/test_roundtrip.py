from pytoon import dumps, loads


def test_roundtrip_simple():
    obj = {"x": 1, "y": "hello", "z": True}
    assert loads(dumps(obj)) == obj


def test_roundtrip_nested():
    obj = {
        "context": {
            "task": "demo",
            "stats": {"a": 1, "b": 2},
        }
    }
    assert loads(dumps(obj)) == obj


def test_roundtrip_primitive_array():
    arr = ["a", "b", "c"]
    assert loads(dumps(arr)) == arr


def test_roundtrip_tabular_array():
    arr = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]
    assert loads(dumps(arr)) == arr
