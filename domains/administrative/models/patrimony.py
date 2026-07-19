from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from domains.condominium.models.condominium import Condominium
from domains.personalities.models.entity import Entity
from domains.condominium.models.collaborator import Collaborator
from domains.parameters.models import (
    AssetType,
    AssetCategory,
    AssetStatus,
    AssetStateCondition,
    AssetBrand,
    AssetMaintenanceFrequency,
)
from core.services.validators import validate_date
from domains.administrative.validators.validators import (
    validate_file_size_10mb,
    validate_photo_extension,
    validate_invoice_extension,
    validate_manual_extension,
    validate_warranty_extension,
)

class Patrimony(models.Model):
    # Aba: Principal
    condominium = models.ForeignKey(
        Condominium,
        on_delete=models.SET_NULL,
        related_name="patrimonies",
        verbose_name="Condomínio",
        null=True,
        blank=True,
    )
    release_date = models.DateField(
        validators=[validate_date],
        null=False,
        blank=False,
        verbose_name="Data de Lançamento",
    )
    asset_code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código do Patrimônio",
    )
    name = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Nome do Patrimônio",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descrição",
    )
    asset_type = models.ForeignKey(
        AssetType,
        on_delete=models.PROTECT,
        related_name="patrimonies_by_type",
        null=False,
        blank=False,
        verbose_name="Tipo de Patrimônio",
    )
    asset_category = models.ForeignKey(
        AssetCategory,
        on_delete=models.PROTECT,
        related_name="patrimonies_by_category",
        null=False,
        blank=False,
        verbose_name="Categoria de Patrimônio",
    )
    location = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Localização",
    )
    asset_status = models.ForeignKey(
        AssetStatus,
        on_delete=models.PROTECT,
        related_name="patrimonies_by_status",
        null=False,
        blank=False,
        verbose_name="Status do Patrimônio",
    )
    state_condition = models.ForeignKey(
        AssetStateCondition,
        on_delete=models.PROTECT,
        related_name="patrimonies_by_condition",
        null=False,
        blank=False,
        verbose_name="Estado de Conservação",
    )
    serial_number = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name="Número de Série",
    )
    asset_brand = models.ForeignKey(
        AssetBrand,
        on_delete=models.SET_NULL,
        related_name="patrimonies_by_brand",
        null=True,
        blank=True,
        verbose_name="Marca do Patrimônio",
    )
    asset_model = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Modelo",
    )
    quantity = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Quantidade",
    )

    # Aba: Aquisições
    acquisition_date = models.DateField(
        null=False,
        blank=False,
        verbose_name="Data de Aquisição",
    )
    invoice_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Número da Nota Fiscal",
    )
    supplier = models.ForeignKey(
        Entity,
        on_delete=models.SET_NULL,
        related_name="patrimonies_by_supplier",
        null=True,
        blank=True,
        verbose_name="Entidades",
    )
    purchase_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Valor de Compra",
    )
    current_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Valor Atual",
    )
    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Taxa de Depreciação",
    )
    useful_life_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        verbose_name="Vida Útil em Meses",
    )
    warranty_expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Vencimento da Garantia",
    )

    # Aba: Manutenções
    requires_maintenance = models.BooleanField(
        default=False,
        verbose_name="Requer Manutenção",
    )
    maintenance_frequency = models.ForeignKey(
        AssetMaintenanceFrequency,
        on_delete=models.SET_NULL,
        related_name="patrimonies_by_frequency",
        null=True,
        blank=True,
        verbose_name="Frequência de Manutenção",
    )
    last_maintenance_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Última Manutenção",
    )
    next_maintenance_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Próxima Manutenção",
    )
    maintenance_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações de Manutenção",
    )

    # Aba: Documentos
    main_photo = models.ImageField(
        upload_to="administrative/patrimonys/",
        null=True,
        blank=True,
        validators=[validate_file_size_10mb, validate_photo_extension],
        verbose_name="Foto Principal",
    )
    invoice_file = models.FileField(
        upload_to="administrative/patrimonys/",
        null=True,
        blank=True,
        validators=[validate_file_size_10mb, validate_invoice_extension],
        verbose_name="Nota Fiscal",
    )
    manual_file = models.FileField(
        upload_to="administrative/patrimonys/",
        null=True,
        blank=True,
        validators=[validate_file_size_10mb, validate_manual_extension],
        verbose_name="Manual Técnico",
    )
    warranty_file = models.FileField(
        upload_to="administrative/patrimonys/",
        null=True,
        blank=True,
        validators=[validate_file_size_10mb, validate_warranty_extension],
        verbose_name="Certificado de Garantia",
    )

    # Aba: Auditoria
    responsible_person = models.ForeignKey(
        Collaborator,
        on_delete=models.SET_NULL,
        related_name="patrimonies_by_responsible",
        null=True,
        blank=True,
        verbose_name="Responsável",
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
        verbose_name = "06. Patrimônio"
        verbose_name_plural = "06. Patrimônios"
        ordering = ["-created_at", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["asset_code"],
                name="unique_patrimony_asset_code",
            )
        ]
        indexes = [
            models.Index(fields=["asset_code"]),
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["release_date"]),
            models.Index(fields=["acquisition_date"]),
            models.Index(fields=["asset_status"]),
            models.Index(fields=["asset_type"]),
            models.Index(fields=["asset_category"]),
        ]

    def clean(self):
        super().clean()
        if self.last_maintenance_date and self.next_maintenance_date:
            if self.next_maintenance_date < self.last_maintenance_date:
                raise ValidationError({
                    'next_maintenance_date': "A próxima manutenção não pode ser anterior à última manutenção."
                })

    def __str__(self):
        return f"{self.asset_code or 'SEM CÓDIGO'} - {self.name}"
