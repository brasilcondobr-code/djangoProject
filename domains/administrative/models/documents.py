from django.db import models

class Documents(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "03. Documento"
        verbose_name_plural = "03. Documentos"

    def __str__(self):
        return "03. Documentos"
