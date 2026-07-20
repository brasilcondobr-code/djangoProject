from django.db import models

class VirtualAssembly(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "11. Assembleia Virtual"
        verbose_name_plural = "11. Assembleias Virtuais"

    def __str__(self):
        return "11. Assembleias Virtuais"
