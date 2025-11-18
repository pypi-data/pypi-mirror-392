import json
import time
import statistics
from typing import Any, Dict, List
from toon import encode, decode

def generate_tabular_data(rows: int) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "users": [
            {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 50),
                "active": i % 2 == 0
            }
            for i in range(rows)
        ]
    }

def generate_nested_data(rows: int) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "users": [
            {
                "id": i,
                "profile": {
                    "name": f"User{i}",
                    "contact": {
                        "email": f"user{i}@example.com",
                        "phone": f"555-{i:04d}"
                    }
                },
                "scores": [i * 10, i * 10 + 5, i * 10 + 10]
            }
            for i in range(rows)
        ]
    }

def benchmark_encode(func, data: Any, iterations: int = 100) -> float:
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(data)
        end = time.perf_counter()
        times.append((end - start) * 1000)
    return statistics.mean(times)

def benchmark_decode(func, encoded: str, iterations: int = 100) -> float:
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(encoded)
        end = time.perf_counter()
        times.append((end - start) * 1000)
    return statistics.mean(times)

def estimate_tokens(text: str) -> int:
    return len(text.split())

def run_benchmark(name: str, data: Any):
    print(f"\nBenchmark: {name}")
    print("-" * 70)
    
    toon_encoded = encode(data)
    json_encoded = json.dumps(data, separators=(',', ':'))
    
    toon_encode_time = benchmark_encode(encode, data)
    json_encode_time = benchmark_encode(json.dumps, data)
    
    toon_decode_time = benchmark_decode(decode, toon_encoded)
    json_decode_time = benchmark_decode(json.loads, json_encoded)
    
    toon_size = len(toon_encoded)
    json_size = len(json_encoded)
    
    toon_tokens = estimate_tokens(toon_encoded)
    json_tokens = estimate_tokens(json_encoded)
    
    print(f"{'Format':<10} {'Encode (ms)':<12} {'Decode (ms)':<12} {'Size (bytes)':<14} {'Tokens (est.)':<14}")
    print("-" * 70)
    print(f"{'TOON':<10} {toon_encode_time:<12.2f} {toon_decode_time:<12.2f} {toon_size:<14} {toon_tokens:<14}")
    print(f"{'JSON':<10} {json_encode_time:<12.2f} {json_decode_time:<12.2f} {json_size:<14} {json_tokens:<14}")
    
    size_reduction = ((json_size - toon_size) / json_size) * 100
    token_reduction = ((json_tokens - toon_tokens) / json_tokens) * 100
    
    print(f"\nTOON vs JSON:")
    print(f"  Size reduction: {size_reduction:.1f}%")
    print(f"  Token reduction: {token_reduction:.1f}%")

if __name__ == "__main__":
    print("TOON Python Benchmarks")
    print("=" * 70)
    
    run_benchmark("Tabular Data (100 rows)", generate_tabular_data(100))
    run_benchmark("Tabular Data (1000 rows)", generate_tabular_data(1000))
    run_benchmark("Nested Data (100 rows)", generate_nested_data(100))
    
    print("\n" + "=" * 70)
    print("Note: Token counts are estimates. Actual tokenization may vary.")

