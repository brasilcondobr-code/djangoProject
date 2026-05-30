class CondominiumException(Exception):
    """Base exception for Condominium domain."""
    pass

class CondominiumNotFoundError(CondominiumException):
    """Raised when a Condominium is not found."""
    pass
