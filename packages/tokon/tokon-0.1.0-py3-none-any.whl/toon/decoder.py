from typing import Any, List, Tuple, Optional, Literal
from .exceptions import TOONDecodeError, InvalidDelimiterError

DelimiterType = Literal[",", "\t", "|"]

class TOONDecoder:
    def __init__(self, delimiter: Optional[DelimiterType] = None):
        self.delimiter = delimiter
        self.indent = "  "
    
    def unquote_string(self, value: str) -> str:
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value
    
    def parse_primitive(self, value: str) -> Any:
        value = value.strip()
        if value == "null":
            return None
        elif value == "true":
            return True
        elif value == "false":
            return False
        elif value.startswith('"') and value.endswith('"'):
            return self.unquote_string(value)
        elif value.replace(".", "", 1).replace("-", "", 1).isdigit():
            if "." in value:
                try:
                    return float(value)
                except ValueError:
                    return value
            else:
                try:
                    return int(value)
                except ValueError:
                    return value
        else:
            return self.unquote_string(value)
    
    def parse_table_header(self, line: str) -> Tuple[Optional[str], int, List[str], Optional[str]]:
        line = line.strip()
        if ":" not in line:
            return None, 0, [], None
        
        key_part, _ = line.rsplit(":", 1)
        
        if "[" not in key_part or "{" not in key_part:
            return None, 0, [], None
        
        key_name = key_part.split("[", 1)[0]
        
        bracket_start = key_part.find("[")
        bracket_end = key_part.find("]")
        if bracket_start == -1 or bracket_end == -1:
            return None, 0, [], None
        
        bracket_content = key_part[bracket_start + 1:bracket_end]
        try:
            count = int(bracket_content)
            detected_delimiter = None
        except ValueError:
            if bracket_content in [",", "\t", "|"]:
                detected_delimiter = bracket_content
                count = 0
            else:
                return None, 0, [], None
        
        schema_start = key_part.find("{")
        schema_end = key_part.find("}")
        if schema_start == -1 or schema_end == -1:
            return None, 0, [], None
        
        schema_str = key_part[schema_start + 1:schema_end]
        delimiter_to_use = detected_delimiter or self.delimiter or ","
        schema = [s.strip() for s in schema_str.split(delimiter_to_use) if s.strip()]
        
        return key_name, count, schema, detected_delimiter or self.delimiter or ","
    
    def parse_table_row(self, line: str, schema: List[str], delimiter: str = ",") -> dict:
        line = line.strip()
        values = []
        current_value = []
        in_quotes = False
        i = 0
        
        while i < len(line):
            char = line[i]
            if char == '"' and (i == 0 or line[i-1] != '\\'):
                in_quotes = not in_quotes
                current_value.append(char)
            elif char == delimiter and not in_quotes:
                values.append("".join(current_value).strip())
                current_value = []
            else:
                current_value.append(char)
            i += 1
        
        if current_value:
            values.append("".join(current_value).strip())
        
        if len(values) != len(schema):
            raise TOONDecodeError(f"Row has {len(values)} values but schema expects {len(schema)}")
        
        result = {}
        for key, val in zip(schema, values):
            result[key] = self.parse_primitive(val)
        
        return result
    
    def get_indent_level(self, line: str) -> int:
        indent_count = 0
        for char in line:
            if char == " ":
                indent_count += 1
            elif char == "\t":
                indent_count += 4
            else:
                break
        return indent_count // len(self.indent)
    
    def parse_lines(self, lines: List[str], start: int, indent_level: int) -> Tuple[Any, int]:
        if start >= len(lines):
            return None, start
        
        line = lines[start]
        line_indent = self.get_indent_level(line)
        
        if line_indent < indent_level:
            return None, start
        
        stripped = line.strip()
        if not stripped:
            return self.parse_lines(lines, start + 1, indent_level)
        
        key_name, count, schema, delimiter = self.parse_table_header(stripped)
        if key_name and schema:
            result = []
            current = start + 1
            expected_indent = indent_level + 1
            
            for _ in range(count):
                if current >= len(lines):
                    break
                row_line = lines[current]
                row_indent = self.get_indent_level(row_line)
                
                if row_indent < expected_indent:
                    break
                
                if row_indent == expected_indent:
                    row_data = self.parse_table_row(row_line.strip(), schema, delimiter)
                    result.append(row_data)
                    current += 1
                else:
                    current += 1
            
            return result, current
        
        if ":" in stripped and not stripped.startswith("-"):
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            if not value:
                current = start + 1
                obj_result = {}
                expected_indent = indent_level + 1
                
                while current < len(lines):
                    next_line = lines[current]
                    next_indent = self.get_indent_level(next_line)
                    
                    if next_indent < expected_indent:
                        break
                    
                    if next_indent == expected_indent:
                        if next_line.strip().startswith("- "):
                            arr_val, current = self.parse_lines(lines, current, expected_indent)
                            obj_result[key] = arr_val
                        else:
                            nested_key, nested_val, current = self.parse_key_value(lines, current, expected_indent)
                            if nested_key is None:
                                break
                            obj_result[nested_key] = nested_val
                    else:
                        current += 1
                
                return obj_result, current
            else:
                return self.parse_primitive(value), start + 1
        
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            
            result_array = []
            current = start
            expected_indent = indent_level
            
            while current < len(lines):
                line = lines[current]
                line_indent = self.get_indent_level(line)
                
                if line_indent < expected_indent:
                    break
                
                if line_indent == expected_indent:
                    if line.strip().startswith("- "):
                        item_val_str = line.strip()[2:].strip()
                        
                        if item_val_str and ":" in item_val_str and not item_val_str.startswith('"'):
                            peek_current = current + 1
                            has_nested = False
                            if peek_current < len(lines):
                                peek_line = lines[peek_current]
                                peek_indent = self.get_indent_level(peek_line)
                                if peek_indent == expected_indent + 1 and not peek_line.strip().startswith("- "):
                                    has_nested = True
                            
                            if has_nested:
                                nested_obj = {}
                                nested_current = current
                                
                                while nested_current < len(lines):
                                    nested_line = lines[nested_current]
                                    nested_indent = self.get_indent_level(nested_line)
                                    
                                    if nested_indent < expected_indent:
                                        break
                                    
                                    if nested_indent == expected_indent:
                                        if nested_line.strip().startswith("- "):
                                            break
                                        item_line_val = nested_line.strip()[2:].strip() if nested_line.strip().startswith("- ") else nested_line.strip()
                                        if ":" in item_line_val and not item_line_val.startswith('"'):
                                            item_key, item_val = item_line_val.split(":", 1)
                                            item_key = item_key.strip()
                                            item_val = item_val.strip()
                                            if not item_val:
                                                nested_key, nested_val, nested_current = self.parse_key_value(lines, nested_current + 1, expected_indent + 1)
                                                if nested_key:
                                                    nested_obj[item_key] = {nested_key: nested_val}
                                                else:
                                                    nested_obj[item_key] = {}
                                                continue
                                            else:
                                                nested_obj[item_key] = self.parse_primitive(item_val)
                                        else:
                                            nested_key, nested_val, nested_current = self.parse_key_value(lines, nested_current, expected_indent + 1)
                                            if nested_key is None:
                                                break
                                            nested_obj[nested_key] = nested_val
                                        nested_current += 1
                                    elif nested_indent > expected_indent:
                                        nested_key, nested_val, nested_current = self.parse_key_value(lines, nested_current, expected_indent + 1)
                                        if nested_key is None:
                                            break
                                        nested_obj[nested_key] = nested_val
                                    else:
                                        nested_current += 1
                                
                                result_array.append(nested_obj)
                                current = nested_current
                            else:
                                item_key, item_val = item_val_str.split(":", 1)
                                item_key = item_key.strip()
                                item_val = item_val.strip()
                                
                                if not item_val:
                                    result_array.append({item_key: {}})
                                else:
                                    result_array.append({item_key: self.parse_primitive(item_val)})
                                current += 1
                        else:
                            item_val = self.parse_primitive(item_val_str)
                            result_array.append(item_val)
                            current += 1
                    else:
                        break
                else:
                    current += 1
            
            if result_array:
                return result_array, current
            
            return self.parse_primitive(value), start + 1
        
        return self.parse_primitive(stripped), start + 1
    
    def parse_key_value(self, lines: List[str], start: int, indent_level: int) -> Tuple[str, Any, int]:
        if start >= len(lines):
            return None, None, start
        
        line = lines[start]
        line_indent = self.get_indent_level(line)
        
        if line_indent < indent_level:
            return None, None, start
        
        stripped = line.strip()
        if not stripped:
            return self.parse_key_value(lines, start + 1, indent_level)
        
        if ":" not in stripped:
            return None, None, start
        
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        
        if not value:
            current = start + 1
            expected_indent = indent_level + 1
            
            if current < len(lines):
                next_line = lines[current]
                next_indent = self.get_indent_level(next_line)
                
                if next_indent >= expected_indent and next_line.strip().startswith("- "):
                    arr_val, current = self.parse_lines(lines, current, expected_indent)
                    return key, arr_val, current
            
            obj_result = {}
            
            while current < len(lines):
                next_line = lines[current]
                next_indent = self.get_indent_level(next_line)
                
                if next_indent < expected_indent:
                    break
                
                if next_indent == expected_indent:
                    if next_line.strip().startswith("- "):
                        arr_val, current = self.parse_lines(lines, current, expected_indent)
                        obj_result[key] = arr_val
                    else:
                        nested_key, nested_val, current = self.parse_key_value(lines, current, expected_indent)
                        if nested_key is None:
                            break
                        obj_result[nested_key] = nested_val
                else:
                    current += 1
            
            return key, obj_result, current
        
        parsed_value = self.parse_primitive(value)
        return key, parsed_value, start + 1
    
    def decode(self, s: str) -> Any:
        s = s.strip()
        if not s:
            raise TOONDecodeError("Empty string cannot be decoded")
        
        lines = s.split("\n")
        
        first_line = lines[0].strip() if lines else ""
        key_name, count, schema, delimiter = self.parse_table_header(first_line)
        
        if key_name and schema:
            result = {}
            current = 0
            expected_indent = 0
            
            table_data = []
            current = 1
            
            for _ in range(count):
                if current >= len(lines):
                    break
                row_line = lines[current]
                row_indent = self.get_indent_level(row_line)
                
                if row_indent < 1:
                    break
                
                if row_indent == 1:
                    row_data = self.parse_table_row(row_line.strip(), schema, delimiter)
                    table_data.append(row_data)
                    current += 1
                else:
                    current += 1
            
            result[key_name] = table_data
            return result
        
        result = {}
        current = 0
        
        while current < len(lines):
            line = lines[current]
            if not line.strip():
                current += 1
                continue
            
            key, value, current = self.parse_key_value(lines, current, 0)
            if key is None:
                break
            result[key] = value
        
        if not result:
            result, _ = self.parse_lines(lines, 0, 0)
        
        return result

def decode(s: str, delimiter: Optional[DelimiterType] = None) -> Any:
    decoder = TOONDecoder(delimiter=delimiter)
    return decoder.decode(s)
