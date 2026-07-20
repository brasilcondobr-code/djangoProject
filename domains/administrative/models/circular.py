from django.db import models
from core.services.validators import validate_date
from domains.email_service.models import ConnectionStatus, SMTPConfiguration
from domains.residents.models import CondominiumUnit
from domains.parameters.models import ResidentType

class Circular(models.Model):
    # Aba: Principal
    condominium = models.ManyToManyField(
        CondominiumUnit,
        related_name="circulars",
        verbose_name="Condomínio",
        blank=True,
    )
    types_residents = models.ManyToManyField(
        ResidentType,
        related_name="circulars",
        verbose_name="Tipos de Residentes",
        blank=True,
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

    # Aba: Configurações
    email_smtp_configuration = models.ForeignKey(
        SMTPConfiguration,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="circulars",
        verbose_name="Configuração SMTP",
    )
    logs = models.TextField(
        null=True,
        blank=True,
        verbose_name="Logs",
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
        verbose_name = "03. Circular"
        verbose_name_plural = "03. Circulares"
        ordering = ["-release_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["release_date", "title"],
                name="unique_circular_by_date_title",
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.connection_status:
            status_pendente = ConnectionStatus.objects.filter(status__iexact='Pendente').first()
            if status_pendente:
                self.connection_status = status_pendente
        super().save(*args, **kwargs)
