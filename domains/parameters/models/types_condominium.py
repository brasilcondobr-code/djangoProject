from django.db import models

class TypesCondominium(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = "01. Tipo de Condomínio"
        verbose_name_plural = "01. Tipos de Condomínios"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
        db_table = 'parameters_typescondominium'

    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name="Tipo de Condomínio")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
