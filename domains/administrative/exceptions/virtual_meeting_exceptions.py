from domains.administrative.exceptions.administrative_exceptions import AdministrativeException


class VirtualMeetingException(AdministrativeException):
    """Base exception for the Virtual Meeting domain."""


class VirtualMeetingValidationException(VirtualMeetingException):
    """Raised when a Virtual Meeting violates a domain rule."""


class PendingStatusNotFound(VirtualMeetingException):
    """Raised when no pending AssemblyStatus exists."""


class DuplicateTopicTitle(VirtualMeetingException):
    """Raised when two topics share the same title in the same meeting."""