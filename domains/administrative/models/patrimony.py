from django.db import models

class Patrimony(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "07. Patrimônio"
        verbose_name_plural = "07. Patrimônios"

    def __str__(self):
        return "07. Patrimônios"
