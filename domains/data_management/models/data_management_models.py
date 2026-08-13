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

    class TaskType(models.TextChoices):
        VIRTUAL_MEETING_NOTICE = 'notice', 'Edital de Convocação'
        VIRTUAL_MEETING_VOTING = 'voting', 'Convocação para Votação'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        PROCESSING = 'processing', 'Processando'
        SENT = 'sent', 'Enviado'
        FAILED = 'failed', 'Falhou'
        CANCELED = 'canceled', 'Cancelado'

    virtual_meeting = models.ForeignKey(
        'administrative.VirtualMeeting',
        on_delete=models.CASCADE,
        related_name='scheduled_tasks',
        verbose_name='Votação Virtual',
        null=True,
        blank=True,
    )
    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        verbose_name='Tipo de e-mail',
    )
    scheduled_at = models.DateTimeField(
        verbose_name='Agendado para',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Status',
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name='Tentativas',
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Enviado em',
    )
    last_error = models.TextField(
        blank=True,
        default='',
        verbose_name='Último erro',
    )
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='ID da tarefa Celery',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    class Meta:
        app_label = 'data_management'
        verbose_name = "Tarefa Agendada"
        verbose_name_plural = "Tarefas Agendadas"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['virtual_meeting', 'task_type'],
                name='unique_scheduled_task_virtual_meeting_type',
            ),
        ]

    def __str__(self):
        return f'{self.get_task_type_display()} - {self.virtual_meeting} ({self.get_status_display()})'


class ScheduledTaskRecipient(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        SENT = 'sent', 'Enviado'
        FAILED = 'failed', 'Falhou'
        CANCELED = 'canceled', 'Cancelado'

    task = models.ForeignKey(
        ScheduledTaskModule,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name='Tarefa Agendada',
    )
    resident = models.ForeignKey(
        'residents.Resident',
        on_delete=models.PROTECT,
        related_name='scheduled_task_recipients',
        verbose_name='Morador',
    )
    email = models.EmailField(
        verbose_name='E-mail',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Status',
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Enviado em',
    )
    last_error = models.TextField(
        blank=True,
        default='',
        verbose_name='Último erro',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    class Meta:
        app_label = 'data_management'
        verbose_name = 'Destinatário de Tarefa Agendada'
        verbose_name_plural = 'Destinatários de Tarefas Agendadas'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['task', 'resident'],
                name='unique_scheduled_task_recipient',
            ),
        ]

    def __str__(self):
        return f'{self.email} - {self.get_status_display()}'

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
