import pytest
from toon import decode, TOONDecoder, TOONDecodeError

def test_decode_null():
    assert decode("null") is None

def test_decode_boolean():
    assert decode("true") is True
    assert decode("false") is False

def test_decode_integer():
    assert decode("id: 42") == {"id": 42}
    assert decode("42") == 42

def test_decode_float():
    assert decode("value: 3.14") == {"value": 3.14}
    assert decode("3.14") == 3.14

def test_decode_string():
    assert decode("name: hello") == {"name": "hello"}
    assert decode('name: "hello,world"') == {"name": "hello,world"}

def test_decode_simple_object():
    result = decode("name: John\nage: 30")
    assert isinstance(result, dict)
    assert result["name"] == "John"
    assert result["age"] == 30

def test_decode_nested_object():
    result = decode("user:\n  name: Alice\n  age: 25")
    assert isinstance(result, dict)
    assert isinstance(result["user"], dict)
    assert result["user"]["name"] == "Alice"
    assert result["user"]["age"] == 25

def test_decode_simple_array():
    result = decode("colors:\n  - red\n  - green\n  - blue")
    assert isinstance(result, dict)
    assert result["colors"] == ["red", "green", "blue"]

def test_decode_array_with_mixed_types():
    result = decode("items:\n  - 1\n  - hello\n  - true\n  - null")
    assert result["items"] == [1, "hello", True, None]

def test_decode_table_format():
    result = decode("users[2]{id,name,role}:\n  1,Alice,admin\n  2,Bob,user")
    assert isinstance(result, dict)
    assert len(result["users"]) == 2
    assert result["users"][0]["id"] == 1
    assert result["users"][0]["name"] == "Alice"
    assert result["users"][0]["role"] == "admin"
    assert result["users"][1]["id"] == 2
    assert result["users"][1]["name"] == "Bob"
    assert result["users"][1]["role"] == "user"

def test_decode_table_single_row():
    result = decode("users[1]{id,name,role}:\n  1,Alice,admin")
    assert len(result["users"]) == 1
    assert result["users"][0]["id"] == 1

def test_decode_nested_array():
    result = decode("matrix:\n  - - 1\n    - 2\n  - - 3\n    - 4")
    assert isinstance(result, dict)
    assert isinstance(result["matrix"], list)

def test_decode_object_in_array():
    result = decode("items:\n  - a: 1\n  - b: 2")
    assert isinstance(result["items"], list)
    assert len(result["items"]) == 2

def test_decode_array_in_object():
    result = decode("user:\n  name: Alice\n  scores:\n    - 95\n    - 87")
    assert isinstance(result, dict)
    assert result["user"]["scores"] == [95, 87]

def test_decode_complex_nested_structure():
    toon_str = """users:
  - name: Alice
  - name: Bob
total: 2"""
    result = decode(toon_str)
    assert isinstance(result, dict)
    assert len(result["users"]) == 2
    assert result["users"][0]["name"] == "Alice"
    assert result["total"] == 2

def test_decode_empty_string():
    with pytest.raises(TOONDecodeError):
        decode("")

def test_decode_round_trip_simple():
    from toon import encode
    original = {"name": "John", "age": 30}
    encoded = encode(original)
    decoded = decode(encoded)
    assert decoded == original

def test_decode_round_trip_nested():
    from toon import encode
    original = {"user": {"name": "Alice", "age": 25}}
    encoded = encode(original)
    decoded = decode(encoded)
    assert decoded == original

def test_decode_round_trip_array():
    from toon import encode
    original = {"colors": ["red", "green", "blue"]}
    encoded = encode(original)
    decoded = decode(encoded)
    assert decoded == original

def test_decode_round_trip_table():
    from toon import encode
    original = {"users": [{"id": 1, "name": "Alice", "role": "admin"}, {"id": 2, "name": "Bob", "role": "user"}]}
    encoded = encode(original)
    decoded = decode(encoded)
    assert decoded == original

def test_decode_round_trip_complex():
    from toon import encode
    original = {
        "users": [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ],
        "total": 2
    }
    encoded = encode(original)
    decoded = decode(encoded)
    assert "users" in decoded
    assert len(decoded["users"]) == 2
    assert decoded["users"][0]["name"] in ["Alice", "Bob"]
    if "total" in decoded:
        assert decoded["total"] == 2

def test_decode_string_with_comma():
    result = decode('message: "hello,world"')
    assert result["message"] == "hello,world"

def test_decode_primitive_values():
    assert decode("null") is None
    assert decode("true") is True
    assert decode("false") is False
    assert decode("42") == 42
    assert decode("3.14") == 3.14

def test_decode_multiple_keys():
    result = decode("a: 1\nb: 2\nc: 3")
    assert result == {"a": 1, "b": 2, "c": 3}

def test_decode_empty_object():
    result = decode("empty:")
    assert result == {"empty": {}}

def test_decode_table_with_quoted_strings():
    result = decode('users[1]{name,message}:\n  Alice,"hello,world"')
    assert result["users"][0]["name"] == "Alice"
    assert result["users"][0]["message"] == "hello,world"

def test_decode_nested_object_deep():
    result = decode("level1:\n  level2:\n    level3:\n      value: deep")
    assert result["level1"]["level2"]["level3"]["value"] == "deep"

def test_decode_array_of_objects():
    result = decode("users:\n  - name: Alice\n  - name: Bob")
    assert len(result["users"]) == 2
    assert result["users"][0]["name"] == "Alice"
    assert result["users"][1]["name"] == "Bob"
