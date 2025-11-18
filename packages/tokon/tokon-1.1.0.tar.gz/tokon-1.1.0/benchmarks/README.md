# Tokon Benchmarks

Performance and token efficiency benchmarks for Tokon v1.1.

## Running Benchmarks

```bash
python benchmarks/tokon_benchmark.py
```

## Results

### Token Efficiency

| Format | Tokens | Reduction vs JSON |
|--------|--------|-------------------|
| JSON | 180 | - |
| Tokon-H | 85 | 53% |
| Tokon-C | 40 | 78% |

### Performance

- Encoding speed: Comparable to JSON
- Decoding speed: Comparable to JSON
- Memory usage: Efficient for large datasets

## Methodology

1. Test payload: ~180 JSON tokens
2. GPT tokenizer used for accurate counts
3. Symbols chosen for single-token behavior
4. Repeated keys fully collapsed

## Custom Benchmarks

```python
from tokon import encode, decode
import json

data = {"name": "Alice", "age": 30}

# Compare sizes
json_str = json.dumps(data)
tokon_h = encode(data, mode='h')
tokon_c = encode(data, mode='c')

print(f"JSON: {len(json_str)} chars")
print(f"Tokon-H: {len(tokon_h)} chars")
print(f"Tokon-C: {len(tokon_c)} chars")
```
