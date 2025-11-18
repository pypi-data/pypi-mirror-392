from typing import Union, Dict, List, Any, Optional
from enum import Enum

class TOONType(Enum):
    STRING = "s"
    INTEGER = "i"
    FLOAT = "f"
    BOOLEAN = "b"
    NULL = "n"
    OBJECT = "o"
    ARRAY = "a"

TOONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

