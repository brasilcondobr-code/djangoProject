from django.db import models

class ImportModule(models.Model):
    
    class Meta:
        verbose_name = '01. Importação'
        verbose_name_plural = '01. Importações'
        
    def __str__(self):
        return "01. Importações"

class ExportModule(models.Model):
    
    class Meta:
        verbose_name = '02. Exportação'
        verbose_name_plural = '02. Exportações'
        
    def __str__(self):
        return "02. Exportações"
        
       
class AuditModule(models.Model):
    
    class Meta:
        verbose_name = '03. Auditoria'
        verbose_name_plural = '03. Auditorias'
        
    def __str__(self):
        return "03. Auditorias"
        
class ScheduledTaskModule(models.Model):
    
    class Meta:
        verbose_name = '04. Tarefa Agendada'
        verbose_name_plural = '04. Tarefas Agendadas'
        
    def __str__(self):
        return "04. Tarefas Agendadas"
        
class IntegrationModule(models.Model):
    
    class Meta:
        verbose_name = '05. Integração'
        verbose_name_plural = '05. Integrações'
        
    def __str__(self):
        return "05. Integrações"

class BackupModule(models.Model):
    
    class Meta:
        verbose_name = '06. Backup'
        verbose_name_plural = '06. Backups'
        
    def __str__(self):
        return "06. Backups"
        
class RestoreModule(models.Model):
    
    class Meta:
        verbose_name = '07. Restauração'
        verbose_name_plural = '07. Restaurações'
        
    def __str__(self):
        return "07. Restaurações"
