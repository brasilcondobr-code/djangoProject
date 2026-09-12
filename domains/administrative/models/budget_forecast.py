from django.db import models

class BudgetForecast(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "08. Previsão Orçamentária"
        verbose_name_plural = "08. Previsões Orçamentárias"

    def __str__(self):
        return "08. Previsões Orçamentárias"
