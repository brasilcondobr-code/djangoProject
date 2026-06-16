from django.db import models
from core.services.validators import validate_date
from domains.condominium.models import Condominium
from domains.email_service.models import ConnectionStatus, SMTPConfiguration
from domains.parameters.models import ResidentType
from domains.residents.models import Resident

class Circular(models.Model):
    # Aba: Principal
    condominium = models.ForeignKey(
        Condominium,
        on_delete=models.CASCADE,
        related_name="circulars",
        verbose_name="Condomínio",
    )

    release_date = models.DateField(
        validators=[validate_date],
        verbose_name="Data de Lançamento",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )

    circular_content = models.TextField(
        verbose_name="Conteúdo da Circular",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
    )

    connection_status = models.ForeignKey(
        ConnectionStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="circulars",
        verbose_name="Status",
    )

    # Aba: Moradores
    types_residents = models.ForeignKey(
        ResidentType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="circulars",
        verbose_name="Tipo de Residente",
    )

    residents = models.ManyToManyField(
        Resident,
        blank=True,
        related_name="circulars",
        verbose_name="Residentes",
    )

    # Aba: Configurações
    email_smtp_configuration = models.ForeignKey(
        SMTPConfiguration,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="circulars",
        verbose_name="Configuração SMTP",
    )

    # Auditoria
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
        verbose_name = "02. Circular"
        verbose_name_plural = "02. Circulares"
        ordering = ["-release_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["condominium", "release_date", "title"],
                name="unique_circular_by_condominium_date_title",
            ),
        ]

    def __str__(self):
        return self.title
