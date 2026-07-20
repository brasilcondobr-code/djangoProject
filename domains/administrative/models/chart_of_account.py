from django.db import models

class ChartOfAccount(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "09. Plano de Conta"
        verbose_name_plural = "09. Plano de Contas"

    def __str__(self):
        return "09. Plano de Contas"
