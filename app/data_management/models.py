from django.db import models

class ImportModule(models.Model):
    
    class Meta:
        verbose_name = '1. Importação'
        verbose_name_plural = '1. Importações'

class ExportModule(models.Model):
    
    class Meta:
        verbose_name = '2. Exportação'
        verbose_name_plural = '2. Exportações'
        
class LogModule(models.Model):
    
    class Meta:
        verbose_name = '3. Log'
        verbose_name_plural = '3. Logs'
        
class AuditModule(models.Model):
    
    class Meta:
        verbose_name = '4. Auditoria'
        verbose_name_plural = '4. Auditorias'
        
class ScheduledTaskModule(models.Model):
    
    class Meta:
        verbose_name = '5. Tarefa Agendada'
        verbose_name_plural = '5. Tarefas Agendadas'
        
class IntegrationModule(models.Model):
    
    class Meta:
        verbose_name = '6. Integração'
        verbose_name_plural = '6. Integrações'

class BackupModule(models.Model):
    
    class Meta:
        verbose_name = '7. Backup'
        verbose_name_plural = '7. Backups'
        
class RestoreModule(models.Model):
    
    class Meta:
        verbose_name = '8. Restauração'
        verbose_name_plural = '8. Restaurações'
