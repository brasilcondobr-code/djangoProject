from domains.system.models import (
    TechnicalSupportTicket, SystemLog, AutomatedRoutine, Training, 
    IntegrationToken, ConnectedUser
)

class SystemRepository:
    @staticmethod
    def get_all_technical_support_tickets():
        return TechnicalSupportTicket.objects.all()

    @staticmethod
    def get_all_system_logs():
        return SystemLog.objects.all()

    @staticmethod
    def get_all_automated_routines():
        return AutomatedRoutine.objects.all()

    @staticmethod
    def get_all_trainings():
        return Training.objects.all()

    @staticmethod
    def get_all_integration_tokens():
        return IntegrationToken.objects.all()

    @staticmethod
    def get_all_connected_users():
        return ConnectedUser.objects.all()
