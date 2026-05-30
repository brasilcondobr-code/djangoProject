from django.db import models

class Circular(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "02. Circular"
        verbose_name_plural = "02. Circulares"

    def __str__(self):
        return "02. Circulares"
