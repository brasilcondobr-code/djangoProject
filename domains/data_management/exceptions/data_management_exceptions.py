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


class ExportException(DataManagementException):
    """Base exception for the Export module."""


class ExportPermanentFailure(ExportException):
    """
    Base para falhas PERMANENTES (não recuperáveis): não devem gerar retry.

    Ex.: serviço de exportação inexistente, formato inválido, validação de
    caminho/arquivo. A tarefa Celery apenas marca FAILED e encerra.
    """


class ExportValidationException(ExportPermanentFailure):
    """Raised when an export value fails domain validation."""


class ExportFileNotFound(ExportValidationException):
    """Raised when the referenced export file does not exist or is invalid."""


class ExportServiceNotFound(ExportPermanentFailure):
    """Raised when the export_service is not registered in the registry."""


class ExportInvalidState(ExportPermanentFailure):
    """Raised when an operation is not allowed for the current export status."""


class ExportAlreadyProcessing(ExportException):
    """Raised when an export is requested while another is QUEUED/PROCESSING."""
