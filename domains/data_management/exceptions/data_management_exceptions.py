class DataManagementException(Exception):
    """Base exception for DataManagement domain."""
    pass


class BackupException(DataManagementException):
    """Base exception for the Backup module."""


class BackupValidationException(BackupException):
    """Raised when a backup value fails domain validation (date, path, file)."""


class BackupFileNotFound(BackupValidationException):
    """Raised when the referenced backup file does not exist or is invalid."""


class BackupInvalidState(BackupException):
    """Raised when an operation is not allowed for the current backup status."""


class BackupAlreadyRunning(BackupException):
    """Raised when the same backup is already being executed concurrently."""


class BackupRestoreInProgress(BackupException):
    """Raised when a restore is requested while another restore is running."""


class BackupExecutionException(BackupException):
    """Raised when the external backup/restore script fails or times out."""
