from django.db import models
from django.utils.translation import gettext_lazy as _

class DocumentType(models.Model):
    description = models.CharField(
        verbose_name=_('Descrição'),
        max_length=255,
        unique=True,
        null=False,
        blank=False
    )
    is_active = models.BooleanField(
        verbose_name=_('Ativo'),
        default=True
    )

    class Meta:
        verbose_name = _('Tipo de Documento')
        verbose_name_plural = _('07. Tipos de Documentos')
        unique_together = [
            ('description',),
        ]
        ordering = [
            'description'
        ]

    def __str__(self):
        return self.description
