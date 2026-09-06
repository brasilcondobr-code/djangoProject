from django.contrib import admin
from .models import (TechnicalSupportTicket, SystemLog, AutomatedRoutine, Training, IntegrationToken, ConnectedUser)

@admin.register(TechnicalSupportTicket)
class TechnicalSupportTicketAdmin(admin.ModelAdmin):
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
    list_display = (
        "user",
        "user_email",
        "is_connected",
        "last_activity",
        "connected_at",
        "disconnected_at",
    )
    list_filter = ("is_connected", "user__is_staff", "user__is_active")
    search_fields = ("user__username", "user__email")
    ordering = ("-last_activity",)
    exclude = ("session_key",)
    readonly_fields = (
        "user",
        "connected_at",
        "last_activity",
        "disconnected_at",
        "is_connected",
        "ip_address",
        "user_agent",
        "created_at",
        "updated_at",
    )

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "E-mail"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
