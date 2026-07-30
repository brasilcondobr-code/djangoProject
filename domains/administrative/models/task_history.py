from django.db import models
from django.conf import settings


class TaskHistory(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = 'Histórico da Tarefa'
        verbose_name_plural = 'Históricos da Tarefa'
        ordering = ['-history_date', '-created_at']
        db_table = 'administrative_task_history'
        indexes = [
            models.Index(fields=['task', 'history_date']),
            models.Index(fields=['created_by_user']),
        ]

    task = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,
        related_name='histories',
        verbose_name='Tarefa',
    )
    history_date = models.DateField(
        verbose_name='Data do histórico',
    )
    description_history = models.TextField(
        verbose_name='Descrição do histórico',
    )
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_task_histories',
        verbose_name='Criado por',
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
        return f'Histórico #{self.pk} - {self.history_date}'
