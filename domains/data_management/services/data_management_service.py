from domains.data_management.repositories import DataManagementRepository
from domains.data_management.selectors import DataManagementSelector

class DataManagementService:
    @staticmethod
    def get_all_import_modules():
        return DataManagementSelector.get_all_import_modules()

    @staticmethod
    def get_all_export_modules():
        return DataManagementSelector.get_all_export_modules()

    @staticmethod
    def get_all_log_modules():
        return DataManagementSelector.get_all_log_modules()

    @staticmethod
    def get_all_audit_modules():
        return DataManagementSelector.get_all_audit_modules()

    @staticmethod
    def get_all_scheduled_task_modules():
        return DataManagementSelector.get_all_scheduled_task_modules()

    @staticmethod
    def get_all_integration_modules():
        return DataManagementSelector.get_all_integration_modules()

    @staticmethod
    def get_all_backup_modules():
        return DataManagementSelector.get_all_backup_modules()

    @staticmethod
    def get_all_restore_modules():
        return DataManagementSelector.get_all_restore_modules()
