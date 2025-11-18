class TokonError(Exception):
    """Base exception for all Tokon errors"""
    pass


class TokonSyntaxError(TokonError):
    """Invalid Tokon syntax"""
    def __init__(self, message: str, line: int = None, column: int = None):
        super().__init__(message)
        self.line = line
        self.column = column
        if line is not None:
            self.message = f"Line {line}" + (f", column {column}" if column else "") + f": {message}"
        else:
            self.message = message

    def __str__(self):
        return self.message


class TokonSchemaError(TokonError):
    """Schema validation or loading error"""
    pass


class TokonTypeError(TokonError):
    """Type mismatch error"""
    pass


class TokonDecodeError(TokonError):
    """Error during decoding"""
    pass


class TokonEncodeError(TokonError):
    """Error during encoding"""
    pass

