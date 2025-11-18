"""
Tokon Compact Engine

Optimizes Tokon-C encoding for maximum token efficiency.
"""

from typing import Any, Dict, List
from .encoder import TokonEncoder
from .schema import TokonSchema


class CompactEngine:
    """Engine for optimizing compact mode encoding"""
    
    def __init__(self, schema: TokonSchema):
        self.schema = schema
        self.encoder = TokonEncoder(mode='c', schema=schema)
    
    def optimize(self, data: Any) -> str:
        """Optimize encoding for maximum compactness"""
        return self.encoder.encode(data)
    
    def minimize_symbols(self, data: Any) -> str:
        """Minimize symbol usage by reusing common patterns"""
        encoded = self.encoder.encode(data)
        return self._compress_whitespace(encoded)
    
    def _compress_whitespace(self, s: str) -> str:
        """Remove unnecessary whitespace"""
        import re
        s = re.sub(r'\s+', ' ', s)
        s = s.replace(' [', '[').replace('] ', ']')
        return s.strip()

