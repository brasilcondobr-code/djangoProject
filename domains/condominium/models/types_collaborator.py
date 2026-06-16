from django.db import models

class TypesCollaborator(models.Model):
    class Meta:
        app_label = 'condominium'
        verbose_name = "02. Tipo de Colaborador"
        verbose_name_plural = "02. Tipos de Colaboradores"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
        db_table = 'condominium_types_collaborators'

    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name="Tipo de Colaborador")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
