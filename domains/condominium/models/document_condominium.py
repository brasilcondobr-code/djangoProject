from django.db import models
from .condominium import Condominium

class DocumentCondominium(models.Model):
    class Meta:
        app_label = 'condominium'
        verbose_name = "04. Documento do Condomínio"
        verbose_name_plural = "04. Documentos do Condomínio"
        ordering = ["name", "created_at"]
        db_table = 'condominium_documentcondominium'

    condominium = models.ForeignKey(Condominium, related_name="documents", null=False, blank=False, verbose_name="Condomínio", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome do Documento")
    file = models.FileField(upload_to='condominium/documents/', null=False, blank=False, verbose_name="Arquivo do Documento")
    observations = models.TextField(null=True, blank=True, verbose_name="Observações")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
