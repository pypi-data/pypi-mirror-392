"""
Tokon Decoder

Decodes Tokon-H (human-readable) or Tokon-C (compact) format to Python objects.
Auto-detects mode based on content.
"""

import re
from typing import Any, Dict, List, Optional, Literal, Tuple
from .exceptions import TokonDecodeError, TokonSyntaxError
from .schema import TokonSchema, get_schema

Mode = Literal['h', 'c', 'auto']


class TokonDecoder:
    """Decoder for Tokon format"""
    
    def __init__(self, mode: Mode = 'auto', schema: Optional[TokonSchema] = None, indent: str = "  "):
        if mode not in ['h', 'c', 'auto']:
            raise TokonDecodeError(f"Invalid mode: {mode}. Must be 'h', 'c', or 'auto'")
        
        self.mode = mode
        self.schema = schema
        self.indent = indent
    
    def decode(self, s: str) -> Any:
        """Decode Tokon string to Python object"""
        s = s.strip()
        if not s:
            raise TokonDecodeError("Empty string cannot be decoded")
        
        detected_mode = self._detect_mode(s) if self.mode == 'auto' else self.mode
        
        if detected_mode == 'c':
            return self._decode_compact(s)
        else:
            return self._decode_human(s)
    
    def _detect_mode(self, s: str) -> str:
        """Auto-detect mode (H or C)"""
        s = s.strip()
        
        if s.startswith('[') or '[' in s[:50]:
            return 'c'
        
        if ':' in s and not any(c in s for c in ['\n  ', '\n\t']):
            if re.match(r'^\w+:\w+', s):
                return 'c'
        
        return 'h'
    
    def _decode_human(self, s: str) -> Any:
        """Decode Tokon-H format"""
        lines = [line for line in s.split('\n') if line.strip()]
        if not lines:
            return {}
        
        result, _ = self._parse_lines_h(lines, 0, 0)
        return result if result is not None else {}
    
    def _decode_compact(self, s: str) -> Any:
        """Decode Tokon-C format"""
        s = s.strip()
        if s.startswith('[') and s.endswith(']'):
            s = s[1:-1]
        
        result = self._parse_compact(s)
        return result
    
    def _parse_lines_h(self, lines: List[str], start: int, indent_level: int) -> Tuple[Any, int]:
        """Parse lines in H-mode"""
        if start >= len(lines):
            return {}, start
        
        result = {}
        i = start
        
        while i < len(lines):
            line = lines[i]
            current_indent = self._get_indent_level(line)
            
            if current_indent < indent_level:
                break
            
            if current_indent == indent_level:
                stripped = line.strip()
                if not stripped:
                    i += 1
                    continue
                
                if ' ' in stripped:
                    parts = stripped.split(' ', 1)
                    key = parts[0]
                    if len(parts) == 2:
                        value_str = parts[1]
                        value = self._parse_primitive_h(value_str)
                        result[key] = value
                        i += 1
                    else:
                        key = parts[0]
                        nested_value, next_i = self._parse_nested_h(lines, i + 1, indent_level + 1)
                        result[key] = nested_value
                        i = next_i
                else:
                    key = stripped
                    nested_value, next_i = self._parse_nested_h(lines, i + 1, indent_level + 1)
                    result[key] = nested_value
                    i = next_i
            else:
                i += 1
        
        return result, i
    
    def _parse_nested_h(self, lines: List[str], start: int, indent_level: int) -> Tuple[Any, int]:
        """Parse nested structure in H-mode"""
        if start >= len(lines):
            return {}, start
        
        first_line = lines[start]
        first_indent = self._get_indent_level(first_line)
        
        if first_indent < indent_level:
            return [], start
        
        if first_indent == indent_level:
            stripped = first_line.strip()
            
            peek_ahead = start + 1
            has_more_at_same_indent = False
            if peek_ahead < len(lines):
                next_line = lines[peek_ahead]
                next_indent = self._get_indent_level(next_line)
                if next_indent == indent_level:
                    has_more_at_same_indent = True
            
            if has_more_at_same_indent:
                if ' ' in stripped:
                    parts = stripped.split(' ', 1)
                    first_key = parts[0]
                    first_value = parts[1] if len(parts) > 1 else ""
                else:
                    first_key = None
                    first_value = None
                
                next_stripped = lines[peek_ahead].strip()
                if ' ' in next_stripped:
                    next_parts = next_stripped.split(' ', 1)
                    next_key = next_parts[0]
                else:
                    next_key = None
                
                if first_key and next_key and first_key != next_key:
                    is_array = False
                elif not first_key and not next_key:
                    is_array = True
                elif first_key and not next_key:
                    is_array = True
                elif not first_key and next_key:
                    is_array = False
                else:
                    is_array = False
                
                if is_array:
                    items = []
                    i = start
                    
                    while i < len(lines):
                        line = lines[i]
                        line_indent = self._get_indent_level(line)
                        
                        if line_indent < indent_level:
                            break
                        
                        if line_indent == indent_level:
                            stripped = line.strip()
                            if ' ' in stripped:
                                parts = stripped.split(' ', 1)
                                value_str = parts[1] if len(parts) > 1 else ""
                                value = self._parse_primitive_h(value_str) if value_str else None
                                items.append(value)
                            else:
                                value = self._parse_primitive_h(stripped)
                                items.append(value)
                            i += 1
                        elif line_indent > indent_level:
                            obj, next_i = self._parse_lines_h(lines, i, indent_level)
                            if items and isinstance(items[-1], dict):
                                items[-1].update(obj)
                            else:
                                items.append(obj)
                            i = next_i
                            continue
                        else:
                            break
                    
                    return items, i
                else:
                    obj, next_i = self._parse_lines_h(lines, start, indent_level)
                    return obj, next_i
            else:
                if ' ' in stripped:
                    parts = stripped.split(' ', 1)
                    value_str = parts[1] if len(parts) > 1 else ""
                    value = self._parse_primitive_h(value_str) if value_str else None
                    return value, start + 1
                else:
                    peek_next = start + 1
                    if peek_next < len(lines):
                        next_line = lines[peek_next]
                        next_indent = self._get_indent_level(next_line)
                        if next_indent > indent_level:
                            obj, next_i = self._parse_lines_h(lines, peek_next, next_indent)
                            return obj, next_i
                        else:
                            return {}, start + 1
                    else:
                        return {}, start + 1
        
        if first_indent > indent_level:
            peek_ahead = start + 1
            is_array = False
            
            if peek_ahead < len(lines):
                next_line = lines[peek_ahead]
                next_indent = self._get_indent_level(next_line)
                
                if next_indent == first_indent:
                    first_stripped = first_line.strip()
                    next_stripped = next_line.strip()
                    
                    first_has_space = ' ' in first_stripped
                    next_has_space = ' ' in next_stripped
                    
                    if first_has_space:
                        first_parts = first_stripped.split(' ', 1)
                        first_key = first_parts[0]
                    else:
                        first_key = None
                    
                    if next_has_space:
                        next_parts = next_stripped.split(' ', 1)
                        next_key = next_parts[0]
                    else:
                        next_key = None
                    
                    if first_has_space and next_has_space:
                        if first_key != next_key:
                            is_array = True
                        else:
                            is_array = False
                    elif not first_has_space and not next_has_space:
                        is_array = True
                    elif first_has_space and not next_has_space:
                        is_array = True
                    elif not first_has_space and next_has_space:
                        is_array = False
                else:
                    first_stripped = first_line.strip()
                    if ' ' not in first_stripped:
                        is_array = True
                    else:
                        is_array = False
            else:
                first_stripped = first_line.strip()
                if ' ' not in first_stripped:
                    is_array = True
                else:
                    is_array = False
            
            if is_array:
                items = []
                i = start
                
                while i < len(lines):
                    line = lines[i]
                    line_indent = self._get_indent_level(line)
                    
                    if line_indent < indent_level:
                        break
                    
                    if line_indent == first_indent:
                        stripped = line.strip()
                        if ' ' in stripped:
                            parts = stripped.split(' ', 1)
                            value_str = parts[1] if len(parts) > 1 else ""
                            value = self._parse_primitive_h(value_str) if value_str else None
                            items.append(value)
                        else:
                            value = self._parse_primitive_h(stripped)
                            items.append(value)
                        i += 1
                    elif line_indent > first_indent:
                        peek_further = next_i = i + 1
                        if peek_further < len(lines):
                            further_line = lines[peek_further]
                            further_indent = self._get_indent_level(further_line)
                            if further_indent == first_indent:
                                obj, next_i = self._parse_lines_h(lines, i, first_indent)
                                if items and isinstance(items[-1], list):
                                    items[-1].append(obj)
                                elif items and isinstance(items[-1], dict):
                                    items[-1].update(obj)
                                else:
                                    items.append(obj)
                                i = next_i
                                continue
                        
                        obj, next_i = self._parse_lines_h(lines, i, first_indent)
                        if items and isinstance(items[-1], dict):
                            items[-1].update(obj)
                        else:
                            items.append(obj)
                        i = next_i
                        continue
                    else:
                        break
                
                return items, i
            else:
                obj, next_i = self._parse_lines_h(lines, start, indent_level)
                return obj, next_i
        
        obj, next_i = self._parse_lines_h(lines, start, indent_level)
        return obj, next_i
    
    def _parse_compact(self, s: str) -> Any:
        """Parse compact format"""
        s = s.strip()
        if not s:
            return {}
        
        if s.startswith('[') and s.endswith(']'):
            s = s[1:-1]
            return self._parse_array_c(s)
        
        parts = self._split_compact(s)
        
        if len(parts) == 1 and ':' not in parts[0] and '[' not in parts[0]:
            return self._parse_primitive_c(parts[0])
        
        result = {}
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if '[' in part and not part.startswith('['):
                bracket_pos = part.find('[')
                key_part = part[:bracket_pos]
                value_part = part[bracket_pos:]
                if ':' in key_part:
                    key, _ = key_part.split(':', 1)
                    key = self._get_field(key.strip())
                else:
                    key = self._get_field(key_part.strip())
                result[key] = self._parse_compact(value_part)
            elif ':' in part and not part.startswith('['):
                key, value = part.split(':', 1)
                key = self._get_field(key.strip())
                value = value.strip()
                if value.startswith('['):
                    result[key] = self._parse_compact(value)
                else:
                    result[key] = self._parse_primitive_c(value)
            elif part.startswith('['):
                nested = self._parse_compact(part)
                if isinstance(nested, list) and len(nested) == 1 and isinstance(nested[0], dict):
                    result.update(nested[0])
                elif isinstance(nested, dict):
                    result.update(nested)
                else:
                    return nested
            else:
                return self._parse_primitive_c(part)
        
        return result if result else {}
    
    def _parse_array_c(self, s: str) -> List[Any]:
        """Parse array in C-mode"""
        s = s.strip()
        if not s:
            return []
        
        parts = self._split_compact(s)
        result = []
        
        for part in parts:
            part = part.strip()
            if part.startswith('['):
                result.append(self._parse_compact(part))
            elif ':' in part:
                key, value = part.split(':', 1)
                key = self._get_field(key.strip())
                value = value.strip()
                if value.startswith('['):
                    result.append({key: self._parse_compact(value)})
                else:
                    result.append({key: self._parse_primitive_c(value)})
            else:
                result.append(self._parse_primitive_c(part))
        
        return result
    
    def _split_compact(self, s: str) -> List[str]:
        """Split compact string into parts, handling nested brackets"""
        parts = []
        current = []
        depth = 0
        i = 0
        
        while i < len(s):
            char = s[i]
            
            if char == '[':
                depth += 1
                current.append(char)
            elif char == ']':
                depth -= 1
                current.append(char)
            elif char == ' ' and depth == 0:
                if current:
                    parts.append(''.join(current))
                    current = []
            else:
                current.append(char)
            
            i += 1
        
        if current:
            parts.append(''.join(current))
        
        return parts
    
    def _parse_primitive_h(self, value_str: str) -> Any:
        """Parse primitive value in H-mode"""
        value_str = value_str.strip()
        
        if value_str == "null":
            return None
        elif value_str == "true":
            return True
        elif value_str == "false":
            return False
        elif value_str.startswith('"') and value_str.endswith('"'):
            return self._unescape_string(value_str[1:-1])
        elif value_str.replace('.', '', 1).replace('-', '', 1).isdigit():
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        else:
            return value_str
    
    def _parse_primitive_c(self, value_str: str) -> Any:
        """Parse primitive value in C-mode"""
        value_str = value_str.strip()
        
        if value_str == "null":
            return None
        elif value_str == "1":
            return True
        elif value_str == "0":
            return False
        elif value_str.startswith('"') and value_str.endswith('"'):
            return self._unescape_string(value_str[1:-1])
        elif value_str.replace('.', '', 1).replace('-', '', 1).isdigit():
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        else:
            return value_str
    
    def _get_field(self, symbol: str) -> str:
        """Get field name from symbol, or return symbol if no schema"""
        if self.schema:
            field = self.schema.get_field(symbol)
            if field:
                return field
        return symbol
    
    def _get_indent_level(self, line: str) -> int:
        """Get indentation level"""
        indent_count = 0
        for char in line:
            if char == ' ':
                indent_count += 1
            elif char == '\t':
                indent_count += len(self.indent)
            else:
                break
        return indent_count // len(self.indent)
    
    def _unescape_string(self, value: str) -> str:
        """Unescape string"""
        return value.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')


import re


def decode(s: str, mode: Mode = 'auto', schema: Optional[TokonSchema] = None) -> Any:
    """Decode Tokon string to Python object"""
    decoder = TokonDecoder(mode=mode, schema=schema)
    return decoder.decode(s)

