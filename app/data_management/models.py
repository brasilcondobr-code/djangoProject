from django.db import models

class ImportModule(models.Model):
    
    class Meta:
        verbose_name = '1. Importação'
        verbose_name_plural = '1. Importações'
        
    def __str__(self):
        return "Importações"

class ExportModule(models.Model):
    
    class Meta:
        verbose_name = '2. Exportação'
        verbose_name_plural = '2. Exportações'
        
    def __str__(self):
        return "Exportações"
        
class LogModule(models.Model):
    
    class Meta:
        verbose_name = '3. Log'
        verbose_name_plural = '3. Logs'
        
    def __str__(self):
        return "Logs"
        
class AuditModule(models.Model):
    
    class Meta:
        verbose_name = '4. Auditoria'
        verbose_name_plural = '4. Auditorias'
        
    def __str__(self):
        return "Auditorias"
        
class ScheduledTaskModule(models.Model):
    
    class Meta:
        verbose_name = '5. Tarefa Agendada'
        verbose_name_plural = '5. Tarefas Agendadas'
        
    def __str__(self):
        return "Tarefas Agendadas"
        
class IntegrationModule(models.Model):
    
    class Meta:
        verbose_name = '6. Integração'
        verbose_name_plural = '6. Integrações'
        
    def __str__(self):
        return "Integrações"

class BackupModule(models.Model):
    
    class Meta:
        verbose_name = '7. Backup'
        verbose_name_plural = '7. Backups'
        
    def __str__(self):
        return "Backups"
        
class RestoreModule(models.Model):
    
    class Meta:
        verbose_name = '8. Restauração'
        verbose_name_plural = '8. Restaurações'
        
    def __str__(self):
        return "Restaurações"
