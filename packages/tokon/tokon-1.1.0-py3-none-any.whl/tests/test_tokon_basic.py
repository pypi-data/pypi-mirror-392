"""
Basic tests for Tokon v1.1
"""

import pytest
from tokon import encode, decode, TokonEncoder, TokonDecoder


def test_encode_decode_human_mode():
    """Test basic encode/decode in human mode"""
    data = {
        "name": "Alice",
        "age": 30,
        "active": True
    }
    
    tokon_h = encode(data, mode='h')
    assert "name" in tokon_h
    assert "Alice" in tokon_h
    assert "age" in tokon_h
    assert "30" in tokon_h
    
    decoded = decode(tokon_h, mode='h')
    assert decoded["name"] == "Alice"
    assert decoded["age"] == 30
    assert decoded["active"] == True


def test_encode_decode_compact_mode():
    """Test basic encode/decode in compact mode"""
    data = {
        "name": "Alice",
        "age": 30,
        "active": True
    }
    
    tokon_c = encode(data, mode='c')
    assert "[" in tokon_c or ":" in tokon_c
    
    decoded = decode(tokon_c, mode='c')
    assert decoded["name"] == "Alice"
    assert decoded["age"] == 30
    assert decoded["active"] == True


def test_nested_object_h():
    """Test nested objects in H-mode"""
    data = {
        "user": {
            "name": "Alice",
            "age": 30
        }
    }
    
    tokon_h = encode(data, mode='h')
    decoded = decode(tokon_h, mode='h')
    
    assert decoded["user"]["name"] == "Alice"
    assert decoded["user"]["age"] == 30


def test_array_h():
    """Test arrays in H-mode"""
    data = {
        "tags": ["python", "ai", "serialization"]
    }
    
    tokon_h = encode(data, mode='h')
    decoded = decode(tokon_h, mode='h')
    
    assert decoded["tags"] == ["python", "ai", "serialization"]


def test_auto_detect_mode():
    """Test auto-detection of mode"""
    data_h = {
        "name": "Alice",
        "age": 30
    }
    
    data_c = {
        "name": "Alice",
        "age": 30
    }
    
    tokon_h = encode(data_h, mode='h')
    tokon_c = encode(data_c, mode='c')
    
    decoded_h = decode(tokon_h, mode='auto')
    decoded_c = decode(tokon_c, mode='auto')
    
    assert decoded_h["name"] == "Alice"
    assert decoded_c["name"] == "Alice"


def test_primitive_types():
    """Test all primitive types"""
    data = {
        "string": "hello",
        "integer": 42,
        "float": 3.14,
        "boolean_true": True,
        "boolean_false": False,
        "null": None
    }
    
    tokon_h = encode(data, mode='h')
    decoded = decode(tokon_h, mode='h')
    
    assert decoded["string"] == "hello"
    assert decoded["integer"] == 42
    assert decoded["float"] == 3.14
    assert decoded["boolean_true"] == True
    assert decoded["boolean_false"] == False
    assert decoded["null"] is None

