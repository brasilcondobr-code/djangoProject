from django.db import models
from .condominium_unit import CondominiumUnit

class Documents(models.Model):
    class Meta:
        app_label = 'residents'
        ordering = ["condo_unit", "title", "created_at"]
        verbose_name = "08. Documento"
        verbose_name_plural = "08. Documentos"
        unique_together = (("condo_unit", "title"), ("condo_unit", "document_type", "created_at"))
        db_table = 'residents_documents'


    DOCTYPES_CHOICES = [
        ('personal', 'Documentos Pessoais'),
        ('cadastral', 'Cadastrais'),
        ('contracts', 'Contratos'),
        ('receipts', 'Comprovantes'),
        ('TAX', 'Documentos Fiscais'),
        ('vehicle_data', 'Dados de veículos'),
        ('animal_data', 'Dados de animais'),
        ('other', 'Outros'),
    ]
    condo_unit = models.ForeignKey(CondominiumUnit, on_delete=models.CASCADE, related_name="documents", verbose_name="Condomínio/Unidade", null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="Título")
    document_type = models.CharField(max_length=20, choices=DOCTYPES_CHOICES, default='personal', verbose_name="Tipo de documento")
    file = models.FileField(upload_to='documents/', null=True, blank=True, verbose_name="Arquivo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

