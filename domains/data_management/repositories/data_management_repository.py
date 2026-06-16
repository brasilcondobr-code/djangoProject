from domains.data_management.models import (
    ImportModule, ExportModule, LogModule, AuditModule, 
    ScheduledTaskModule, IntegrationModule, BackupModule, RestoreModule
)

class DataManagementRepository:
    @staticmethod
    def get_all_import_modules():
        return ImportModule.objects.all()

    @staticmethod
    def get_all_export_modules():
        return ExportModule.objects.all()

    @staticmethod
    def get_all_log_modules():
        return LogModule.objects.all()

    @staticmethod
    def get_all_audit_modules():
        return AuditModule.objects.all()

    @staticmethod
    def get_all_scheduled_task_modules():
        return ScheduledTaskModule.objects.all()

    @staticmethod
    def get_all_integration_modules():
        return IntegrationModule.objects.all()

    @staticmethod
    def get_all_backup_modules():
        return BackupModule.objects.all()

    @staticmethod
    def get_all_restore_modules():
        return RestoreModule.objects.all()
