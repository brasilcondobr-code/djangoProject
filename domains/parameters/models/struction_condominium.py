from django.db import models

class StructionCondominium(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = "02. Estrutura do Condomínio"
        verbose_name_plural = "02. Estruturas dos Condomínios"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
        db_table = 'parameters_structioncondominium'

    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name="Estrutura do Condomínio")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
