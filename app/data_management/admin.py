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
    pass

@admin.register(IntegrationModule)
class IntegrationModuleAdmin(admin.ModelAdmin):
    pass

@admin.register(BackupModule)
class BackupModuleAdmin(admin.ModelAdmin):
    pass

@admin.register(RestoreModule)
class RestoreModuleAdmin(admin.ModelAdmin):
    pass

