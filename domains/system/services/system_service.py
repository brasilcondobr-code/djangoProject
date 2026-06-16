from domains.system.repositories import SystemRepository
from domains.system.selectors import SystemSelector

class SystemService:
    @staticmethod
    def get_all_technical_support_tickets():
        return SystemSelector.get_all_technical_support_tickets()

    @staticmethod
    def get_all_system_logs():
        return SystemSelector.get_all_system_logs()

    @staticmethod
    def get_all_automated_routines():
        return SystemSelector.get_all_automated_routines()

    @staticmethod
    def get_all_trainings():
        return SystemSelector.get_all_trainings()

    @staticmethod
    def get_all_integration_tokens():
        return SystemSelector.get_all_integration_tokens()

    @staticmethod
    def get_all_connected_users():
        return SystemSelector.get_all_connected_users()
