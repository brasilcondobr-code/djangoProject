from django.db import models

class Patrimony(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "06. Patrimônio"
        verbose_name_plural = "06. Patrimônios"

    def __str__(self):
        return "06. Patrimônios"
