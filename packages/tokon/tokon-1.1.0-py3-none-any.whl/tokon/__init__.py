"""
Tokon v1.1 - Token-Optimized Serialization Format

Dual-mode serialization: Tokon-H (human-readable) and Tokon-C (compact)
"""

from .encoder import encode, TokonEncoder
from .decoder import decode, TokonDecoder
from .schema import load_schema, TokonSchema, SchemaRegistry
from .validator import validate, TokonValidator
from .streaming import TokonStream
from .exceptions import (
    TokonError,
    TokonSyntaxError,
    TokonSchemaError,
    TokonTypeError,
    TokonDecodeError,
    TokonEncodeError,
)

__version__ = "1.1.0"

__all__ = [
    "encode",
    "decode",
    "TokonEncoder",
    "TokonDecoder",
    "load_schema",
    "get_schema",
    "TokonSchema",
    "SchemaRegistry",
    "validate",
    "TokonValidator",
    "TokonStream",
    "CompactEngine",
    "TokonError",
    "TokonSyntaxError",
    "TokonSchemaError",
    "TokonTypeError",
    "TokonDecodeError",
    "TokonEncodeError",
]

