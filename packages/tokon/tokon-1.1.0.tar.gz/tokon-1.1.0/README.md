# Tokon v1.1

**Token-Optimized Serialization Format for AI-Native Applications**

[![PyPI version](https://img.shields.io/pypi/v/tokon)](https://pypi.org/project/tokon/)
[![Python versions](https://img.shields.io/pypi/pyversions/tokon)](https://pypi.org/project/tokon/)
[![License](https://img.shields.io/pypi/l/tokon)](LICENSE)

Tokon is a **dual-mode, schema-driven** data serialization format designed for maximum token efficiency and human readability.

> **Inspired by** the [TOON format](https://github.com/toon-format/toon), but completely redesigned for AI-native workflows with dual-mode architecture and schema-driven optimization.

## Features

- **78% token reduction** vs JSON in compact mode
- **53% token reduction** vs JSON in human mode
- **Dual representation** - readable for humans, compact for LLMs
- **Schema-driven** - stable symbols across projects
- **Type-safe** - built-in validation
- **Streaming-ready** - incremental parsing support
- **Zero dependencies** - pure Python

## Installation

```bash
pip install tokon
```

## Quick Start

```python
from tokon import encode, decode

# Encode to human-readable format
data = {"name": "Alice", "age": 30, "active": True}
tokon_h = encode(data, mode='h')
print(tokon_h)
# name Alice
# age 30
# active true

# Decode back
decoded = decode(tokon_h, mode='h')
```

See [QUICK_START.md](QUICK_START.md) for more examples.

## Modes

### Tokon-H (Human Mode)
Clean, readable format:
```
user
  name Alice
  age 30
  active true
```

### Tokon-C (Compact Mode)
Ultra-compact with schemas:
```
u[n:Alice a:30 x:1]
```

## Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[INSTALLATION.md](INSTALLATION.md)** - Installation guide
- **[USAGE.md](USAGE.md)** - Complete usage guide
- **[TOKON_SPEC.md](TOKON_SPEC.md)** - Full specification
- **[KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)** - Edge cases

## Command Line

```bash
# Encode JSON to Tokon
echo '{"name": "Alice"}' | tokon encode -m h

# Decode Tokon to JSON
echo 'name Alice' | tokon decode
```

## Performance

- **Token Efficiency**: 53-78% reduction vs JSON
- **Speed**: Comparable to JSON
- **Memory**: Efficient for large datasets

## Requirements

- Python 3.8+
- No dependencies

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Version

**Tokon v1.1.0** - Production Ready
