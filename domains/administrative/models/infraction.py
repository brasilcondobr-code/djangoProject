from django.db import models
 
from domains.residents.models import CondominiumUnit
from domains.parameters.models import InfractionsType, ResidentType
from domains.email_service.models import ConnectionStatus, SMTPConfiguration
from domains.administrative.validators import validate_infraction_file_extension
from shared.validators import validate_date
 
class Infraction(models.Model):
    condominium = models.ManyToManyField(
        CondominiumUnit,
        related_name="infractions",
        verbose_name="Condomínio",
        blank=True,
    )
    types_residents = models.ManyToManyField(
        ResidentType,
        related_name="infractions",
        verbose_name="Tipos de Residentes",
        blank=True,
    )


    releaseDate = models.DateField(
        validators=[validate_date],
        blank=True,
        null=True,
        verbose_name="Data de Lançamento",
    )

    infractions_type = models.ForeignKey(
        InfractionsType,
        on_delete=models.CASCADE,
        related_name="infractions",
        verbose_name="Tipo de Infração",
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Título",
    )

    infractionContent = models.TextField(
        null=True,
        blank=True,
        verbose_name="Conteúdo da Infração",
    )

    file = models.FileField(
        upload_to="administrative/infractions/",
        null=True,
        blank=True,
        verbose_name="Documento",
        validators=[validate_infraction_file_extension],
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
        verbose_name="Status",
    )

    email_smtp_configuration = models.ForeignKey(
        SMTPConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infractions",
        verbose_name="Configuração SMTP",
    )
    logs = models.TextField(
        null=True,
        blank=True,
        verbose_name="Logs",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
        null=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
        null=True,
    )

    class Meta:
        verbose_name = "05. Infração"
        verbose_name_plural = "05. Infrações"
        ordering = ["-releaseDate", "title"]
        indexes = [
            models.Index(fields=["releaseDate"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title if self.title else f"Infração {self.id}"

    def save(self, *args, **kwargs):
        if not self.connection_status:
            status_pendente = ConnectionStatus.objects.filter(status__iexact='Pendente').first()
            if status_pendente:
                self.connection_status = status_pendente
        super().save(*args, **kwargs)
