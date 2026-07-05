from django.db import models

class BudgetForecast(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "07. Previsão Orçamentária"
        verbose_name_plural = "07. Previsões Orçamentárias"

    def __str__(self):
        return "07. Previsões Orçamentárias"
