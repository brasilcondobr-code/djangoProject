from django.db import models

class AssetMaintenanceFrequency(models.Model):
    description = models.CharField(
        max_length=255,
        verbose_name="Descrição",
        unique=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        app_label = 'parameters'
        verbose_name = "12. Frequência de Manutenção"
        verbose_name_plural = "12. Frequências de Manutenção"
        ordering = ["description"]

    def __str__(self):
        return self.description
