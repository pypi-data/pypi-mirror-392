"""
Tokon Schema System

Handles .tks schema files, symbol mapping, type definitions, and multilingual support.
"""

import re
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from .exceptions import TokonSchemaError


class SchemaRegistry:
    """Registry for managing multiple schemas"""
    
    def __init__(self):
        self.schemas: Dict[str, 'TokonSchema'] = {}
    
    def register(self, name: str, schema: 'TokonSchema'):
        """Register a schema"""
        self.schemas[name] = schema
    
    def get(self, name: str) -> Optional['TokonSchema']:
        """Get a schema by name"""
        return self.schemas.get(name)
    
    def clear(self):
        """Clear all schemas"""
        self.schemas.clear()


_global_registry = SchemaRegistry()


class TokonSchema:
    """Tokon schema definition"""
    
    def __init__(self, name: str):
        self.name = name
        self.symbols: Dict[str, str] = {}  # field_name -> symbol
        self.reverse_symbols: Dict[str, str] = {}  # symbol -> field_name
        self.types: Dict[str, str] = {}  # field_name -> type
        self.languages: Dict[str, Dict[str, str]] = {}  # lang -> {field: translation}
        self.defaults: Dict[str, Any] = {}
        self.required: List[str] = []
    
    def add_symbol(self, field: str, symbol: str):
        """Add a symbol mapping"""
        if symbol in self.reverse_symbols and self.reverse_symbols[symbol] != field:
            raise TokonSchemaError(f"Symbol '{symbol}' already mapped to '{self.reverse_symbols[symbol]}'")
        self.symbols[field] = symbol
        self.reverse_symbols[symbol] = field
    
    def get_symbol(self, field: str) -> Optional[str]:
        """Get symbol for a field"""
        return self.symbols.get(field)
    
    def get_field(self, symbol: str) -> Optional[str]:
        """Get field name for a symbol"""
        return self.reverse_symbols.get(symbol)
    
    def add_type(self, field: str, type_str: str):
        """Add type definition"""
        self.types[field] = type_str
    
    def get_type(self, field: str) -> Optional[str]:
        """Get type for a field"""
        return self.types.get(field)
    
    def add_language(self, lang: str, translations: Dict[str, str]):
        """Add language translations"""
        self.languages[lang] = translations
    
    def translate(self, field: str, lang: str) -> Optional[str]:
        """Translate field name to language"""
        if lang in self.languages:
            return self.languages[lang].get(field)
        return None
    
    def add_default(self, field: str, value: Any):
        """Add default value"""
        self.defaults[field] = value
    
    def validate_type(self, field: str, value: Any) -> bool:
        """Validate value against field type"""
        type_str = self.get_type(field)
        if not type_str:
            return True
        
        if type_str == "str":
            return isinstance(value, str)
        elif type_str == "int":
            return isinstance(value, int)
        elif type_str == "float":
            return isinstance(value, (int, float))
        elif type_str == "bool":
            return isinstance(value, bool)
        elif type_str == "null":
            return value is None
        elif type_str.startswith("list["):
            return isinstance(value, list)
        elif type_str == "object":
            return isinstance(value, dict)
        
        return True


def parse_schema_file(filepath: Union[str, Path]) -> TokonSchema:
    """Parse a .tks schema file"""
    path = Path(filepath)
    if not path.exists():
        raise TokonSchemaError(f"Schema file not found: {filepath}")
    
    content = path.read_text(encoding='utf-8')
    return parse_schema(content, name=path.stem)


def parse_schema(content: str, name: str = "default") -> TokonSchema:
    """Parse schema from string content"""
    schema = TokonSchema(name)
    
    lines = content.split('\n')
    current_section = None
    current_lang = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line or line.startswith('#'):
            i += 1
            continue
        
        if line.startswith('schema '):
            match = re.match(r'schema\s+(\w+)', line)
            if match:
                schema.name = match.group(1)
        
        elif line == 'symbols {' or line == 'symbols{':
            current_section = 'symbols'
        
        elif line == 'types {' or line == 'types{':
            current_section = 'types'
        
        elif line.startswith('languages {'):
            current_section = 'languages'
        
        elif line.startswith('defaults {'):
            current_section = 'defaults'
        
        elif line.startswith('required {'):
            current_section = 'required'
        
        elif line == '}' and current_section:
            if current_section == 'languages' and current_lang:
                current_lang = None
            current_section = None
        
        elif current_section == 'symbols':
            match = re.match(r'(\w+)\s*→\s*(\w+)', line)
            if match:
                field, symbol = match.groups()
                schema.add_symbol(field, symbol)
        
        elif current_section == 'types':
            match = re.match(r'(\w+):\s*(\S+)', line)
            if match:
                field, type_str = match.groups()
                schema.add_type(field, type_str)
        
        elif current_section == 'languages':
            if ':' in line and '{' not in line:
                match = re.match(r'(\w+):\s*\{', line)
                if match:
                    current_lang = match.group(1)
                    if current_lang not in schema.languages:
                        schema.languages[current_lang] = {}
            elif current_lang and ':' in line:
                match = re.match(r'(\w+):\s*"([^"]+)"', line)
                if match:
                    field, translation = match.groups()
                    schema.languages[current_lang][field] = translation
        
        elif current_section == 'defaults':
            match = re.match(r'(\w+):\s*(.+)', line)
            if match:
                field, value_str = match.groups()
                value = parse_default_value(value_str.strip())
                schema.add_default(field, value)
        
        elif current_section == 'required':
            field = line.strip().rstrip(',')
            if field:
                schema.required.append(field)
        
        i += 1
    
    return schema


def parse_default_value(value_str: str) -> Any:
    """Parse default value string"""
    value_str = value_str.strip().rstrip(',')
    
    if value_str == 'true':
        return True
    elif value_str == 'false':
        return False
    elif value_str == 'null':
        return None
    elif value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    elif value_str.replace('.', '', 1).replace('-', '', 1).isdigit():
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    
    return value_str


def load_schema(filepath: Union[str, Path]) -> TokonSchema:
    """Load a schema from file and register it"""
    schema = parse_schema_file(filepath)
    _global_registry.register(schema.name, schema)
    return schema


def get_schema(name: str) -> Optional[TokonSchema]:
    """Get a registered schema"""
    return _global_registry.get(name)

