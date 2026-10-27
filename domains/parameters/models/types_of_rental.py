from django.core.validators import MinValueValidator
from django.db import models


class TypesOfRental(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '27. Tipo de Locação'
        verbose_name_plural = '27. Tipos de Locações'
        ordering = ['description']
        db_table = 'parameters_typesofrentals'

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

    numberOfAppointments = models.IntegerField(
        verbose_name='Quantidade Agendamentos',
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )

    numberOfReservations = models.IntegerField(
        verbose_name='Quantidade Reservas',
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
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
