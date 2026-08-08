from django.db import models


class AssemblyStatus(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '23. Status da Assembleia'
        verbose_name_plural = '23. Status das Assembleias'
        ordering = ['description']
        db_table = 'parameters_assemblystatus'
        constraints = [
            models.UniqueConstraint(
                fields=['is_running'],
                condition=models.Q(is_running=True),
                name='unique_running_assembly_status',
                violation_error_message='Já existe um status marcado como "Em execução".',
            ),
            models.UniqueConstraint(
                fields=['is_complete'],
                condition=models.Q(is_complete=True),
                name='unique_complete_assembly_status',
                violation_error_message='Já existe um status marcado como "Completo".',
            ),
        ]

    description = models.CharField(
        verbose_name='Descrição',
        max_length=255,
        unique=True,
        null=False,
        blank=False,
    )

    is_pending = models.BooleanField(
        verbose_name='Está pendente',
        default=True,
    )

    is_running = models.BooleanField(
        verbose_name='Está em execução',
        default=False,
    )

    is_complete = models.BooleanField(
        verbose_name='Está completo',
        default=False,
    )

    is_active = models.BooleanField(
        verbose_name='Ativo',
        default=True,
    )

    created_at = models.DateTimeField(
        verbose_name='Criado em',
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name='Atualizado em',
        auto_now=True,
    )

    def __str__(self):
        return self.description