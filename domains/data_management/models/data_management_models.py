from django.db import models

class ImportModule(models.Model):
    class Meta:
        app_label = 'data_management'
        verbose_name = "Importação"
        verbose_name_plural = "Importações"

    def __str__(self):
        return "Importação"

class ExportModule(models.Model):
    class Meta:
        app_label = 'data_management'
        verbose_name = "Exportação"
        verbose_name_plural = "Exportações"

    def __str__(self):
        return "Exportação"

class LogModule(models.Model):
    class Meta:
        app_label = 'data_management'
        verbose_name = "Log"
        verbose_name_plural = "Logs"

    def __str__(self):
        return "Log"

class AuditModule(models.Model):
    class Meta:
        app_label = 'data_management'
        verbose_name = "Auditoria"
        verbose_name_plural = "Auditorias"

    def __str__(self):
        return "Auditoria"

class ScheduledTaskModule(models.Model):
    class Meta:
        app_label = 'data_management'
        verbose_name = "Tarefa Agendada"
        verbose_name_plural = "Tarefas Agendadas"

    def __str__(self):
        return "Tarefa Agendada"

class IntegrationModule(models.Model):
    class Meta:
        app_label = 'data_management'
        verbose_name = "Integração"
        verbose_name_plural = "Integrações"

    def __str__(self):
        return "Integração"

class BackupModule(models.Model):
    class Meta:
        app_label = 'data_management'
        verbose_name = "Backup"
        verbose_name_plural = "Backups"

    def __str__(self):
        return "Backup"

class RestoreModule(models.Model):
    class Meta:
        app_label = 'data_management'
        verbose_name = "Restauração"
        verbose_name_plural = "Restaurações"

    def __str__(self):
        return "Restauração"
