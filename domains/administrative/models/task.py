from django.db import models
from django.conf import settings


class Task(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = '10. Tarefa'
        verbose_name_plural = '10. Tarefas'
        ordering = ['-created_at']
        db_table = 'administrative_task'
        constraints = [
            models.UniqueConstraint(
                fields=['condominium', 'title'],
                name='uq_task_condominium_title',
            ),
        ]
        indexes = [
            models.Index(fields=['condominium', 'is_active']),
            models.Index(fields=['responsible_user']),
            models.Index(fields=['status']),
            models.Index(fields=['release_date']),
            models.Index(fields=['estimated_completion_date']),
            models.Index(fields=['completion_date']),
        ]

    condominium = models.ForeignKey(
        'condominium.Condominium',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Condomínio',
    )
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='created_tasks',
        verbose_name='Criado por',
    )
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='responsible_tasks',
        verbose_name='Responsável',
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Título',
    )
    release_date = models.DateField(
        verbose_name='Data de lançamento',
    )
    estimated_completion_date = models.DateField(
        verbose_name='Data prevista de conclusão',
    )
    completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de conclusão',
    )
    description = models.TextField(
        verbose_name='Descrição',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
    )
    status = models.ForeignKey(
        'email_service.ConnectionStatus',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='tasks',
        verbose_name='Status',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    def __str__(self):
        return self.title
