from django.db import models

class InfractionsType(models.Model):
    INFRACTION_TYPE_CHOICES = [
        ('A', 'Advertência'),
        ('M', 'Multa'),
        ('N', 'Notificação'),
    ]

    description = models.CharField(
        verbose_name='Descrição',
        max_length=255,
        unique=True,
        null=False,
        blank=False
    )
    infraction_type = models.CharField(
        verbose_name='Tipo de Infração',
        max_length=30,
        choices=INFRACTION_TYPE_CHOICES,
        null=False,
        blank=False,
        default='N'
    )
    is_active = models.BooleanField(
        verbose_name='Ativo',
        default=True
    )

    class Meta:
        verbose_name = 'Tipo de Infração'
        verbose_name_plural = '08. Tipos de Infrações'
        unique_together = [
            ('description',),
        ]
        ordering = [
            'description',
        ]

    def __str__(self):
        return f"{self.get_infraction_type_display()} - {self.description}"
