"""
Tokon Validator

Validates data against schemas and type definitions.
"""

from typing import Any, Dict, List, Optional
from .exceptions import TokonTypeError, TokonSchemaError
from .schema import TokonSchema


class TokonValidator:
    """Validator for Tokon data"""
    
    def __init__(self, schema: TokonSchema):
        self.schema = schema
    
    def validate(self, data: Any) -> bool:
        """Validate data against schema"""
        try:
            self._validate_value(data, None)
            return True
        except (TokonTypeError, TokonSchemaError):
            return False
    
    def validate_strict(self, data: Any) -> None:
        """Validate data and raise exceptions on errors"""
        if isinstance(data, dict):
            self._validate_object(data)
        elif isinstance(data, list):
            self._validate_array(data, None)
        else:
            self._validate_value(data, None)
    
    def _validate_object(self, obj: Dict[str, Any]):
        """Validate object against schema"""
        for field in self.schema.required:
            if field not in obj:
                raise TokonSchemaError(f"Required field '{field}' is missing")
        
        for key, value in obj.items():
            self._validate_value(value, key)
    
    def _validate_array(self, arr: List[Any], field: Optional[str]):
        """Validate array"""
        if field:
            type_str = self.schema.get_type(field)
            if type_str and type_str.startswith('list['):
                item_type = type_str[5:-1]
                for item in arr:
                    self._validate_value(item, None, expected_type=item_type)
        else:
            for item in arr:
                self._validate_value(item, None)
    
    def _validate_value(self, value: Any, field: Optional[str], expected_type: Optional[str] = None):
        """Validate a value"""
        if field:
            type_str = expected_type or self.schema.get_type(field)
            if type_str:
                if not self.schema.validate_type(field, value):
                    raise TokonTypeError(f"Field '{field}' has invalid type. Expected {type_str}, got {type(value).__name__}")
        
        if isinstance(value, dict):
            self._validate_object(value)
        elif isinstance(value, list):
            self._validate_array(value, field)


def validate(data: Any, schema: TokonSchema) -> bool:
    """Validate data against schema"""
    validator = TokonValidator(schema)
    return validator.validate(data)

