# TOON Python Benchmarks

This directory contains benchmarks comparing TOON with JSON and other serialization formats.

## Running Benchmarks

```bash
python benchmarks/benchmark.py
```

## Results

Benchmarks measure:
- **Encoding time**: Time to convert Python objects to string format
- **Decoding time**: Time to parse string format back to Python objects
- **Size**: Character count of serialized output
- **Token count**: Estimated token count (for LLM usage)

## Example Results

```
Benchmark: Tabular Data (1000 rows)
─────────────────────────────────────
Format    Encode (ms)  Decode (ms)  Size (bytes)  Tokens (est.)
───────────────────────────────────────────────────────────────
TOON      12.3         8.7          15,234        2,456
JSON      15.1         11.2         18,567        3,123
CSV       5.2          3.1          12,890        2,890
```

## Notes

- Token counts are estimates and may vary by tokenizer
- Results depend on data structure and size
- TOON excels with tabular data; JSON may be better for deeply nested structures

