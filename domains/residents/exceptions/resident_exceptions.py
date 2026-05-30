class ResidentException(Exception):
    """Base exception for Resident domain."""
    pass

class ResidentNotFoundError(ResidentException):
    """Raised when a Resident is not found."""
    pass
