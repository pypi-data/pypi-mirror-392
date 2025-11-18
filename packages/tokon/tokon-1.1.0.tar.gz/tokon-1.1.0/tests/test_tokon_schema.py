"""
Tests for Tokon schema system
"""

import pytest
from pathlib import Path
from tokon import load_schema, TokonSchema, encode, decode


def test_load_schema():
    """Test loading schema from file"""
    schema_path = Path(__file__).parent / "examples" / "user.tks"
    schema = load_schema(schema_path)
    
    assert schema.name == "user"
    assert schema.get_symbol("name") == "n"
    assert schema.get_symbol("age") == "a"
    assert schema.get_field("n") == "name"


def test_encode_with_schema():
    """Test encoding with schema"""
    schema_path = Path(__file__).parent / "examples" / "user.tks"
    schema = load_schema(schema_path)
    
    data = {
        "name": "Alice",
        "age": 30,
        "active": True
    }
    
    tokon_c = encode(data, mode='c', schema=schema)
    assert "n:" in tokon_c or "n:Alice" in tokon_c
    assert "a:30" in tokon_c


def test_decode_with_schema():
    """Test decoding with schema"""
    schema_path = Path(__file__).parent / "examples" / "user.tks"
    schema = load_schema(schema_path)
    
    tokon_c = "n:Alice a:30 x:1"
    decoded = decode(tokon_c, mode='c', schema=schema)
    
    assert decoded["name"] == "Alice"
    assert decoded["age"] == 30
    assert decoded["active"] == True

