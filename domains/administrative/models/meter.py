from django.db import models

class Meter(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "05. Medidor"
        verbose_name_plural = "05. Medidores"

    def __str__(self):
        return "05. Medidores"
