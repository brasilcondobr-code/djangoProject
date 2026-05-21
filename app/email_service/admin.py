from django.contrib import admin
from .models import SMTP_Settings, UsageProfiles, ShippingQueue, EmailHistory

@admin.register(SMTP_Settings)
class SMTP_SettingsAdmin(admin.ModelAdmin):
    pass

@admin.register(UsageProfiles)
class UsageProfilesAdmin(admin.ModelAdmin):
    pass

@admin.register(ShippingQueue)
class ShippingQueueAdmin(admin.ModelAdmin):
    pass

@admin.register(EmailHistory)
class EmailHistoryAdmin(admin.ModelAdmin):
    pass
