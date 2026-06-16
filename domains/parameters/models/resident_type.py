from django.db import models

class ResidentType(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name='Tipo de Residente'
        verbose_name_plural='06. Tipos de Residentes'

        unique_together = [
            ('description',)
        ]

        ordering = [
            'description'
        ]
        db_table = 'parameters_residenttype'

    description = models.CharField(
        verbose_name='Descrição',
        max_length=255,
        unique=True,
        null=False,
        blank=False
    )

    is_active = models.BooleanField(
        verbose_name='Ativo',
        default=True
    )

    def __str__(self):
        return self.description
