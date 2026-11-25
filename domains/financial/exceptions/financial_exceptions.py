class FinancialException(Exception):
    """Base exception for Financial domain."""
    pass


class NewReleaseError(FinancialException):
    """Base error for the NewRelease domain."""
    pass


class NewReleaseValidationError(NewReleaseError):
    """Validation error for a NewRelease record."""
    pass


class NewReleaseTransitionError(NewReleaseError):
    """Invalid status transition for a NewRelease record."""
    pass


class CollectionError(FinancialException):
    """Base error for the Collection domain."""
    pass


class CollectionValidationError(CollectionError):
    """Validation error for a Collection record or its operations."""
    pass


class CollectionTransitionError(CollectionError):
    """Invalid status transition for a Collection record."""
    pass
