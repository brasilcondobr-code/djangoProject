from django.db import models


class VotingType(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '22. Tipo de Votação'
        verbose_name_plural = '22. Tipos de Votações'
        ordering = ['description']
        db_table = 'parameters_votingtype'

    description = models.CharField(
        verbose_name='Descrição',
        max_length=255,
        unique=True,
        null=False,
        blank=False,
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