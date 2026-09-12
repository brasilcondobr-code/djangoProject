from django.db import models

from domains.residents.models.condominium_unit import CondominiumUnit
from domains.parameters.models.meter_type import MeterType
from domains.administrative.validators.validators import (
    validate_meter_composition,
    validate_meter_file_extension,
)
from core.services.validators import validate_date

class Meters(models.Model):
    condominium = models.ForeignKey(
        CondominiumUnit,
        on_delete=models.CASCADE,
        related_name="meter_records",
        verbose_name="Condomínio/Unidade",
    )

    releaseDate = models.DateField(
        validators=[validate_date],
        blank=True,
        null=True,
        verbose_name="Data de Lançamento",
    )

    meterType = models.ForeignKey(
        MeterType,
        on_delete=models.CASCADE,
        related_name="meters",
        verbose_name="Tipo de Medidor",
    )

    composition = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        validators=[validate_meter_composition],
        verbose_name="Composição",
        help_text="Informe a competência no formato MM/AAAA.",
    )

    previousValue = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Valor Anterior",
    )

    currentValue = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Valor Atual",
    )

    Consumption = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Consumo",
    )

    Value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor",
    )

    file = models.FileField(
        upload_to="administrative/documents/",
        null=True,
        blank=True,
        verbose_name="Arquivo do Documento",
        validators=[validate_meter_file_extension],
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    class Meta:
        app_label = 'administrative'
        verbose_name = "06. Medidor"
        verbose_name_plural = "06. Medidores"
        ordering = ["-releaseDate", "composition"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "condominium",
                    "meterType",
                    "composition",
                ],
                name="unique_meter_condominium_type_composition",
            )
        ]
        indexes = [
            models.Index(fields=["releaseDate"]),
            models.Index(fields=["composition"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.condominium} - "
            f"{self.meterType} - "
            f"{self.composition}"
        )
