import pytest
from toon import encode, TOONEncoder, TOONEncodeError

def test_encode_null():
    assert encode(None) == "null"

def test_encode_boolean():
    assert encode(True) == "true"
    assert encode(False) == "false"

def test_encode_integer():
    assert encode(42) == "42"
    assert encode(-10) == "-10"
    assert encode(0) == "0"

def test_encode_float():
    assert encode(3.14) == "3.14"
    assert encode(-0.5) == "-0.5"
    assert encode(1.0) == "1.0"

def test_encode_string():
    assert encode("hello") == "hello"
    assert encode("") == ""

def test_encode_string_with_comma():
    result = encode("hello,world")
    assert result == '"hello,world"'

def test_encode_string_that_looks_like_keyword():
    assert encode("null") == '"null"'
    assert encode("true") == '"true"'
    assert encode("false") == '"false"'

def test_encode_simple_object():
    result = encode({"name": "John", "age": 30})
    assert "name:" in result
    assert "age:" in result
    assert "John" in result
    assert "30" in result

def test_encode_nested_object():
    obj = {"user": {"name": "Alice", "age": 25}}
    result = encode(obj)
    assert "user:" in result
    assert "name:" in result
    assert "Alice" in result

def test_encode_simple_array():
    result = encode({"colors": ["red", "green", "blue"]})
    assert "colors:" in result
    assert "- red" in result
    assert "- green" in result
    assert "- blue" in result

def test_encode_array_with_mixed_types():
    result = encode({"items": [1, "hello", True, None]})
    assert "items:" in result
    assert "- 1" in result
    assert "- hello" in result
    assert "- true" in result
    assert "- null" in result

def test_encode_table_format():
    data = {"users": [{"id": 1, "name": "Alice", "role": "admin"}, {"id": 2, "name": "Bob", "role": "user"}]}
    result = encode(data)
    assert "users[2]{id,name,role}:" in result or "users[2]{id,role,name}:" in result or "users[2]{name,id,role}:" in result or "users[2]{name,role,id}:" in result or "users[2]{role,id,name}:" in result or "users[2]{role,name,id}:" in result
    assert "1,Alice,admin" in result or "Alice,1,admin" in result
    assert "2,Bob,user" in result or "Bob,2,user" in result

def test_encode_nested_array():
    data = {"matrix": [[1, 2], [3, 4]]}
    result = encode(data)
    assert "matrix:" in result

def test_encode_object_in_array():
    data = {"items": [{"a": 1}, {"b": 2}]}
    result = encode(data)
    assert "items:" in result

def test_encode_array_in_object():
    data = {"user": {"name": "Alice", "scores": [95, 87]}}
    result = encode(data)
    assert "user:" in result
    assert "scores:" in result
    assert "- 95" in result

def test_encode_complex_nested_structure():
    obj = {
        "users": [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ],
        "total": 2
    }
    result = encode(obj)
    assert "users" in result
    assert "total:" in result
    assert "Alice" in result or "Bob" in result

def test_encode_deterministic():
    obj = {"c": 3, "a": 1, "b": 2}
    result1 = encode(obj)
    result2 = encode(obj)
    assert result1 == result2

def test_encode_root_level_dict():
    result = encode({"a": 1, "b": 2})
    assert "a:" in result
    assert "b:" in result

def test_encode_root_level_list():
    result = encode([1, 2, 3])
    assert "- 1" in result
    assert "- 2" in result
    assert "- 3" in result

def test_encode_table_requires_same_keys():
    data = [{"a": 1}, {"b": 2}]
    result = encode(data)
    assert "-" in result
