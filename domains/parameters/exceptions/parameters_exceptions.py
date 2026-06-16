class ParametersException(Exception):
    """Base exception for Parameters domain."""
    pass

class ParametersNotFoundError(ParametersException):
    """Raised when a Parameter is not found."""
    pass
