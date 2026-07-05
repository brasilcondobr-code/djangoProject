from django.db import models

class VirtualAssembly(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "10. Assembleia Virtual"
        verbose_name_plural = "10. Assembleias Virtuais"

    def __str__(self):
        return "10. Assembleias Virtuais"
