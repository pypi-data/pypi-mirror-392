from typing import Any, List, Set, Optional, Literal
from .exceptions import TOONEncodeError, InvalidDelimiterError

DelimiterType = Literal[",", "\t", "|"]

class TOONEncoder:
    def __init__(self, delimiter: DelimiterType = ","):
        if delimiter not in [",", "\t", "|"]:
            raise InvalidDelimiterError(f"Delimiter must be ',', '\\t', or '|', got {repr(delimiter)}")
        self.delimiter = delimiter
        self.indent = "  "
    
    def needs_quotes(self, value: str) -> bool:
        if not value:
            return False
        if self.delimiter in value:
            return True
        if ":" in value or "-" in value:
            stripped = value.strip()
            if stripped.startswith("- ") or ":" in stripped:
                return True
        if value.strip() in ["null", "true", "false"]:
            return True
        return False
    
    def quote_string(self, value: str) -> str:
        if self.needs_quotes(value):
            return f'"{value}"'
        return value
    
    def encode_primitive(self, value: Any) -> str:
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return self.quote_string(value)
        else:
            raise TOONEncodeError(f"Unsupported primitive type: {type(value)}")
    
    def get_table_schema(self, items: List[dict]) -> tuple[bool, List[str]]:
        if not items:
            return False, []
        if not all(isinstance(item, dict) for item in items):
            return False, []
        if not all(item for item in items):
            return False, []
        
        first_keys = tuple(sorted(items[0].keys()))
        for item in items[1:]:
            if tuple(sorted(item.keys())) != first_keys:
                return False, []
        
        for item in items:
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    return False, []
        
        return True, list(items[0].keys())
    
    def encode_table(self, items: List[dict], schema: List[str], key: str, indent_level: int) -> str:
        lines = []
        indent_str = self.indent * indent_level
        count = len(items)
        
        schema_str = self.delimiter.join(schema)
        if indent_level == 0:
            header = f"{key}[{count}]{{{schema_str}}}:"
        else:
            header = f"{indent_str}{key}[{count}]{{{schema_str}}}:"
        
        lines.append(header)
        
        for item in items:
            row_values = []
            for schema_key in schema:
                val = item[schema_key]
                if isinstance(val, (dict, list)):
                    raise TOONEncodeError("Nested structures not supported in table rows")
                encoded = self.encode_primitive(val)
                row_values.append(encoded)
            row = indent_str + self.indent + self.delimiter.join(row_values)
            lines.append(row)
        
        return "\n".join(lines)
    
    def encode_object(self, obj: dict, indent_level: int = 0, key: str = None) -> str:
        lines = []
        indent_str = self.indent * indent_level
        
        if key:
            if indent_level == 0:
                lines.append(f"{key}:")
            else:
                lines.append(f"{indent_str}{key}:")
        
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TOONEncodeError(f"Object keys must be strings, got {type(k)}")
            
            next_indent = indent_level + 1 if key else indent_level
            
            if isinstance(v, dict):
                lines.append(self.encode_object(v, next_indent, k))
            elif isinstance(v, list):
                is_table, schema = self.get_table_schema(v)
                if is_table:
                    lines.append(self.encode_table(v, schema, k, indent_level))
                else:
                    lines.append(self.encode_array(v, next_indent, k))
            else:
                value_str = self.encode_primitive(v)
                if key:
                    lines.append(f"{indent_str}{self.indent}{k}: {value_str}")
                else:
                    lines.append(f"{indent_str}{k}: {value_str}")
        
        return "\n".join(lines)
    
    def encode_array(self, arr: List[Any], indent_level: int = 0, key: str = None) -> str:
        if key:
            is_table, schema = self.get_table_schema(arr)
            if is_table:
                return self.encode_table(arr, schema, key, indent_level)
        
        lines = []
        indent_str = self.indent * indent_level
        
        if key:
            if indent_level == 0:
                lines.append(f"{key}:")
            else:
                lines.append(f"{indent_str}{key}:")
        
        next_indent = indent_level + 1 if key else indent_level
        
        for item in arr:
            if isinstance(item, dict):
                item_str = self.encode_object(item, next_indent)
                item_lines = item_str.split("\n")
                for i, line in enumerate(item_lines):
                    if line.strip():
                        if i == 0:
                            lines.append(f"{self.indent * next_indent}- {line.lstrip()}")
                        else:
                            lines.append(f"{self.indent * next_indent}{line}")
            elif isinstance(item, list):
                item_str = self.encode_array(item, next_indent)
                item_lines = item_str.split("\n")
                for i, line in enumerate(item_lines):
                    if line.strip():
                        if i == 0:
                            lines.append(f"{self.indent * next_indent}- {line.lstrip()}")
                        else:
                            lines.append(f"{self.indent * next_indent}{line}")
            else:
                value_str = self.encode_primitive(item)
                lines.append(f"{self.indent * next_indent}- {value_str}")
        
        return "\n".join(lines)
    
    def encode(self, value: Any) -> str:
        if isinstance(value, dict):
            return self.encode_object(value, indent_level=0)
        elif isinstance(value, list):
            return self.encode_array(value, indent_level=0)
        else:
            return self.encode_primitive(value)

def encode(value: Any, delimiter: DelimiterType = ",") -> str:
    encoder = TOONEncoder(delimiter=delimiter)
    return encoder.encode(value)
    