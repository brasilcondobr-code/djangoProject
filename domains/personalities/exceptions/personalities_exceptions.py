class PersonalitiesException(Exception):
    """Base exception for Personalities domain."""
    pass

class PersonalitiesNotFoundError(PersonalitiesException):
    """Raised when a Personality entity is not found."""
    pass
