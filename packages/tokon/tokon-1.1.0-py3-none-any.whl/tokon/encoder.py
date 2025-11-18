"""
Tokon Encoder

Encodes Python objects to Tokon-H (human-readable) or Tokon-C (compact) format.
"""

from typing import Any, Dict, List, Optional, Literal
from .exceptions import TokonEncodeError
from .schema import TokonSchema, get_schema

Mode = Literal['h', 'c', 'auto']


class TokonEncoder:
    """Encoder for Tokon format"""
    
    def __init__(self, mode: Mode = 'h', schema: Optional[TokonSchema] = None, indent: str = "  "):
        if mode not in ['h', 'c', 'auto']:
            raise TokonEncodeError(f"Invalid mode: {mode}. Must be 'h', 'c', or 'auto'")
        
        self.mode = mode
        self.schema = schema
        self.indent = indent
    
    def encode(self, value: Any) -> str:
        """Encode a Python value to Tokon"""
        if self.mode == 'c':
            return self._encode_compact(value)
        elif self.mode == 'h':
            return self._encode_human(value)
        else:
            return self._encode_human(value)
    
    def _encode_human(self, value: Any, indent_level: int = 0) -> str:
        """Encode to Tokon-H (human-readable) format"""
        if isinstance(value, dict):
            return self._encode_object_h(value, indent_level)
        elif isinstance(value, list):
            return self._encode_array_h(value, indent_level)
        else:
            return self._encode_primitive_h(value)
    
    def _encode_compact(self, value: Any) -> str:
        """Encode to Tokon-C (compact) format"""
        if isinstance(value, dict):
            return self._encode_object_c(value)
        elif isinstance(value, list):
            return self._encode_array_c(value)
        else:
            return self._encode_primitive_c(value)
    
    def _encode_primitive_h(self, value: Any) -> str:
        """Encode primitive to H-mode"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            if self._needs_quotes_h(value):
                return f'"{self._escape_string(value)}"'
            return value
        else:
            raise TokonEncodeError(f"Unsupported type: {type(value)}")
    
    def _encode_primitive_c(self, value: Any) -> str:
        """Encode primitive to C-mode"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            if self._needs_quotes_c(value):
                return f'"{self._escape_string(value)}"'
            return value
        else:
            raise TokonEncodeError(f"Unsupported type: {type(value)}")
    
    def _encode_object_h(self, obj: Dict[str, Any], indent_level: int = 0) -> str:
        """Encode object to H-mode"""
        if not obj:
            return ""
        
        lines = []
        indent_str = self.indent * indent_level
        
        for key, value in obj.items():
            if not isinstance(key, str):
                raise TokonEncodeError(f"Object keys must be strings, got {type(key)}")
            
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key}")
                nested = self._encode_object_h(value, indent_level + 1)
                if nested:
                    lines.append(nested)
            elif isinstance(value, list):
                if all(not isinstance(item, (dict, list)) for item in value):
                    lines.append(f"{indent_str}{key}")
                    for item in value:
                        item_str = self._encode_primitive_h(item)
                        lines.append(f"{indent_str}{self.indent}{item_str}")
                else:
                    lines.append(f"{indent_str}{key}")
                    for item in value:
                        if isinstance(item, dict):
                            nested = self._encode_object_h(item, indent_level + 1)
                            if nested:
                                lines.append(nested)
                        elif isinstance(item, list):
                            nested = self._encode_array_h(item, indent_level + 1)
                            if nested:
                                lines.append(nested)
                        else:
                            item_str = self._encode_primitive_h(item)
                            lines.append(f"{indent_str}{self.indent}{item_str}")
            elif isinstance(value, list) and not value:
                lines.append(f"{indent_str}{key}")
            else:
                value_str = self._encode_primitive_h(value)
                lines.append(f"{indent_str}{key} {value_str}")
        
        return "\n".join(lines)
    
    def _encode_object_c(self, obj: Dict[str, Any]) -> str:
        """Encode object to C-mode"""
        if not obj:
            return "[]"
        
        parts = []
        for key, value in obj.items():
            if not isinstance(key, str):
                raise TokonEncodeError(f"Object keys must be strings, got {type(key)}")
            
            symbol = self._get_symbol(key)
            
            if isinstance(value, dict):
                nested = self._encode_object_c(value)
                parts.append(f"{symbol}[{nested}]")
            elif isinstance(value, list):
                nested = self._encode_array_c(value)
                parts.append(f"{symbol}[{nested}]")
            else:
                value_str = self._encode_primitive_c(value)
                parts.append(f"{symbol}:{value_str}")
        
        return " ".join(parts)
    
    def _encode_array_h(self, arr: List[Any], indent_level: int = 0) -> str:
        """Encode array to H-mode"""
        if not arr:
            return ""
        
        lines = []
        indent_str = self.indent * indent_level
        
        for item in arr:
            if isinstance(item, dict):
                nested = self._encode_object_h(item, indent_level)
                if nested:
                    lines.append(nested)
            elif isinstance(item, list):
                nested = self._encode_array_h(item, indent_level + 1)
                if nested:
                    nested_lines = nested.split('\n')
                    for nested_line in nested_lines:
                        if nested_line.strip():
                            lines.append(f"{indent_str}{self.indent}{nested_line.lstrip()}")
            else:
                item_str = self._encode_primitive_h(item)
                lines.append(f"{indent_str}{item_str}")
        
        return "\n".join(lines)
    
    def _encode_array_c(self, arr: List[Any]) -> str:
        """Encode array to C-mode"""
        if not arr:
            return ""
        
        parts = []
        for item in arr:
            if isinstance(item, dict):
                parts.append(self._encode_object_c(item))
            elif isinstance(item, list):
                nested = self._encode_array_c(item)
                parts.append(f"[{nested}]")
            else:
                value_str = self._encode_primitive_c(item)
                parts.append(value_str)
        
        return " ".join(parts)
    
    def _get_symbol(self, field: str) -> str:
        """Get symbol for a field, or return field if no schema"""
        if self.schema:
            symbol = self.schema.get_symbol(field)
            if symbol:
                return symbol
        return field
    
    def _needs_quotes_h(self, value: str) -> bool:
        """Check if string needs quotes in H-mode"""
        if not value:
            return False
        if ' ' in value or '\n' in value or '\t' in value:
            return True
        if value in ['true', 'false', 'null']:
            return True
        return False
    
    def _needs_quotes_c(self, value: str) -> bool:
        """Check if string needs quotes in C-mode"""
        if not value:
            return False
        if ' ' in value or '[' in value or ']' in value or ':' in value:
            return True
        return False
    
    def _escape_string(self, value: str) -> str:
        """Escape special characters in string"""
        return value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def encode(value: Any, mode: Mode = 'h', schema: Optional[TokonSchema] = None) -> str:
    """Encode a Python value to Tokon format"""
    encoder = TokonEncoder(mode=mode, schema=schema)
    return encoder.encode(value)

