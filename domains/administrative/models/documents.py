from django.db import models
from django.utils.translation import gettext_lazy as _

from core.services.validators import validate_date
from domains.condominium.models import Condominium
from domains.parameters.models import DocumentType

class Documents(models.Model):
    condominium = models.ForeignKey(
        Condominium,
        on_delete=models.CASCADE,
        related_name="administrative_documents",
        null=True,
        blank=True,
        verbose_name=_("Condomínio"),
    )

    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name="documents",
        null=True,
        blank=True,
        verbose_name=_("Tipo de Documento"),
    )

    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Título do Documento"),
    )

    registration_date = models.DateField(
        validators=[validate_date],
        null=True,
        blank=True,
        verbose_name=_("Data de Registro"),
    )

    file = models.FileField(
        upload_to="administrative/documents/",
        null=True,
        blank=True,
        verbose_name=_("Arquivo do Documento"),
    )

    observations = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Observações"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Ativo"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Criado em"),
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Atualizado em"),
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "administrative"
        verbose_name = _("04. Documento")
        verbose_name_plural = _("04. Documentos")
        ordering = ["title", "created_at"]
        db_table = "administrative_document"
        unique_together = ["condominium", "title", "registration_date"]

    def __str__(self):
        return self.title
