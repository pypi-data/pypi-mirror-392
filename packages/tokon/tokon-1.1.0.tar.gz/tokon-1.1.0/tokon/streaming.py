"""
Tokon Streaming (Tokon-S)

Supports incremental parsing for chunked transmission.
"""

from typing import Any, Optional, List
from .decoder import TokonDecoder
from .exceptions import TokonDecodeError


class TokonStream:
    """Streaming decoder for incremental parsing"""
    
    def __init__(self, mode: str = 'auto', schema=None):
        self.decoder = TokonDecoder(mode=mode, schema=schema)
        self.buffer = ""
        self.complete = False
        self.result: Optional[Any] = None
    
    def feed(self, chunk: str) -> None:
        """Feed a chunk of Tokon data"""
        if self.complete:
            raise TokonDecodeError("Stream already completed")
        
        self.buffer += chunk
        
        try:
            self.result = self.decoder.decode(self.buffer)
            self.complete = True
        except TokonDecodeError:
            pass
    
    def finish(self) -> Any:
        """Finish streaming and return result"""
        if not self.complete:
            if self.buffer.strip():
                self.result = self.decoder.decode(self.buffer)
                self.complete = True
            else:
                raise TokonDecodeError("No data to decode")
        
        return self.result
    
    def reset(self) -> None:
        """Reset the stream"""
        self.buffer = ""
        self.complete = False
        self.result = None

