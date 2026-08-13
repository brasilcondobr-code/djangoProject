from django.contrib import admin
from .models import BackupModule, ImportModule, ExportModule, AuditModule, RestoreModule, ScheduledTaskModule, IntegrationModule

@admin.register(ImportModule)
class ImportModuleAdmin(admin.ModelAdmin):
    pass

@admin.register(ExportModule)
class ExportModuleAdmin(admin.ModelAdmin):
    pass

@admin.register(AuditModule)
class AuditModuleAdmin(admin.ModelAdmin):
    pass

@admin.register(ScheduledTaskModule)
class ScheduledTaskModuleAdmin(admin.ModelAdmin):
    list_display = (
        'virtual_meeting', 'task_type', 'scheduled_at', 'status',
        'attempts', 'sent_at',
    )
    list_filter = ('status', 'task_type', 'scheduled_at')
    search_fields = ('virtual_meeting__title',)
    readonly_fields = (
        'virtual_meeting', 'task_type', 'scheduled_at', 'status', 'attempts',
        'sent_at', 'last_error', 'celery_task_id', 'created_at', 'updated_at',
    )
    ordering = ('-scheduled_at',)
    list_per_page = 25

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(IntegrationModule)
class IntegrationModuleAdmin(admin.ModelAdmin):
    pass

@admin.register(BackupModule)
class BackupModuleAdmin(admin.ModelAdmin):
    pass

@admin.register(RestoreModule)
class RestoreModuleAdmin(admin.ModelAdmin):
    pass

