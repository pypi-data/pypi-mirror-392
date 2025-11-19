class ConslyricParseError(Exception):
    """Raised when there is an error parsing the Conslyric YAML/JSON."""
    pass

class ConslyricValidationError(Exception):
    """Raised when Conslyric data fails schema validation."""
    pass

class ConslyricRuntimeError(Exception):
    """Raised when an error occurs during Conslyric execution."""
    pass

class ConslyricCompileError(Exception):
    """Raised when an error occurs during Conslyric compilation."""
    pass