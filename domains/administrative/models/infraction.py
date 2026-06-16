from django.db import models

class Infraction(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "04. Infração"
        verbose_name_plural = "04. Infrações"

    def __str__(self):
        return "04. Infrações"
