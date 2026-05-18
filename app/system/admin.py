from django.contrib import admin
from .models import (
    TechnicalSupportTicket, EmailConfiguration, SMSConfiguration, 
    WhatsAppSettings, SystemLog, AutomatedRoutine, Training, 
    IntegrationToken, ConnectedUser
)

@admin.register(TechnicalSupportTicket)
class TechnicalSupportTicketAdmin(admin.ModelAdmin):
    pass

@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    pass

@admin.register(SMSConfiguration)
class SMSConfigurationAdmin(admin.ModelAdmin):
    pass

@admin.register(WhatsAppSettings)
class WhatsAppSettingsAdmin(admin.ModelAdmin):
    pass

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    pass

@admin.register(AutomatedRoutine)
class AutomatedRoutineAdmin(admin.ModelAdmin):
    pass

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    pass

@admin.register(IntegrationToken)
class IntegrationTokenAdmin(admin.ModelAdmin):
    pass

@admin.register(ConnectedUser)
class ConnectedUserAdmin(admin.ModelAdmin):
    pass
