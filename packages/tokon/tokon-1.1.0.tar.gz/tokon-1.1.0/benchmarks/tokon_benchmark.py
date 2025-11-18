"""
Tokon Benchmark Suite

Compares JSON, Tokon-H, and Tokon-C for token efficiency and performance.
"""

import json
import time
from typing import Any, Dict
from tokon import encode, decode, load_schema
from pathlib import Path


def count_tokens_estimate(text: str) -> int:
    """Rough estimate of tokens (GPT-style: ~4 chars per token)"""
    return len(text) // 4


def benchmark_encode(data: Any, name: str):
    """Benchmark encoding"""
    print(f"\n{'='*70}")
    print(f"Benchmark: {name}")
    print(f"{'='*70}")
    
    json_str = json.dumps(data, separators=(',', ':'))
    json_tokens = count_tokens_estimate(json_str)
    
    tokon_h = encode(data, mode='h')
    tokon_h_tokens = count_tokens_estimate(tokon_h)
    
    tokon_c = encode(data, mode='c')
    tokon_c_tokens = count_tokens_estimate(tokon_c)
    
    print(f"\nJSON:")
    print(f"  Size: {len(json_str)} chars")
    print(f"  Tokens (est): {json_tokens}")
    print(f"  Preview: {json_str[:100]}...")
    
    print(f"\nTokon-H:")
    print(f"  Size: {len(tokon_h)} chars")
    print(f"  Tokens (est): {tokon_h_tokens}")
    print(f"  Reduction: {((1 - tokon_h_tokens/json_tokens) * 100):.1f}%")
    print(f"  Preview:\n{tokon_h[:200]}...")
    
    print(f"\nTokon-C:")
    print(f"  Size: {len(tokon_c)} chars")
    print(f"  Tokens (est): {tokon_c_tokens}")
    print(f"  Reduction: {((1 - tokon_c_tokens/json_tokens) * 100):.1f}%")
    print(f"  Preview: {tokon_c[:200]}...")
    
    h_savings = ((1 - tokon_h_tokens/json_tokens) * 100)
    c_savings = ((1 - tokon_c_tokens/json_tokens) * 100)
    
    print(f"\nSummary:")
    print(f"  Tokon-H saves {h_savings:.1f}% tokens vs JSON")
    print(f"  Tokon-C saves {c_savings:.1f}% tokens vs JSON")
    print(f"  Tokon-C is {((1 - tokon_c_tokens/tokon_h_tokens) * 100):.1f}% more compact than Tokon-H")


def benchmark_performance(data: Any, name: str, iterations: int = 10000):
    """Benchmark encoding/decoding performance"""
    print(f"\n{'='*70}")
    print(f"Performance: {name}")
    print(f"{'='*70}")
    
    start = time.time()
    for _ in range(iterations):
        json_str = json.dumps(data)
    json_encode_time = time.time() - start
    
    start = time.time()
    for _ in range(iterations):
        json.loads(json_str)
    json_decode_time = time.time() - start
    
    start = time.time()
    for _ in range(iterations):
        tokon_h = encode(data, mode='h')
    tokon_h_encode_time = time.time() - start
    
    start = time.time()
    for _ in range(iterations):
        decode(tokon_h, mode='h')
    tokon_h_decode_time = time.time() - start
    
    start = time.time()
    for _ in range(iterations):
        tokon_c = encode(data, mode='c')
    tokon_c_encode_time = time.time() - start
    
    start = time.time()
    for _ in range(iterations):
        decode(tokon_c, mode='c')
    tokon_c_decode_time = time.time() - start
    
    print(f"\nJSON:")
    print(f"  Encode: {json_encode_time*1000:.2f}ms ({iterations} iterations)")
    print(f"  Decode: {json_decode_time*1000:.2f}ms ({iterations} iterations)")
    
    print(f"\nTokon-H:")
    print(f"  Encode: {tokon_h_encode_time*1000:.2f}ms ({iterations} iterations)")
    print(f"  Decode: {tokon_h_decode_time*1000:.2f}ms ({iterations} iterations)")
    print(f"  vs JSON: {((tokon_h_encode_time/json_encode_time - 1) * 100):+.1f}% encode, {((tokon_h_decode_time/json_decode_time - 1) * 100):+.1f}% decode")
    
    print(f"\nTokon-C:")
    print(f"  Encode: {tokon_c_encode_time*1000:.2f}ms ({iterations} iterations)")
    print(f"  Decode: {tokon_c_decode_time*1000:.2f}ms ({iterations} iterations)")
    print(f"  vs JSON: {((tokon_c_encode_time/json_encode_time - 1) * 100):+.1f}% encode, {((tokon_c_decode_time/json_decode_time - 1) * 100):+.1f}% decode")


def main():
    """Run all benchmarks"""
    
    simple_data = {
        "name": "Alice",
        "age": 30,
        "active": True
    }
    
    nested_data = {
        "user": {
            "name": "Alice",
            "age": 30,
            "email": "alice@example.com"
        },
        "orders": [
            {"id": 12345, "total": 99.99},
            {"id": 12346, "total": 149.50}
        ]
    }
    
    complex_data = {
        "users": [
            {
                "id": 1,
                "name": "Alice",
                "age": 30,
                "tags": ["python", "ai"],
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            },
            {
                "id": 2,
                "name": "Bob",
                "age": 25,
                "tags": ["javascript", "web"],
                "settings": {
                    "theme": "light",
                    "notifications": False
                }
            }
        ]
    }
    
    print("="*70)
    print("TOKON v1.1 BENCHMARK SUITE")
    print("="*70)
    
    benchmark_encode(simple_data, "Simple Object")
    benchmark_encode(nested_data, "Nested Structure")
    benchmark_encode(complex_data, "Complex Data")
    
    benchmark_performance(simple_data, "Simple Object", 10000)
    benchmark_performance(nested_data, "Nested Structure", 5000)
    benchmark_performance(complex_data, "Complex Data", 1000)
    
    print(f"\n{'='*70}")
    print("Benchmark Complete")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

