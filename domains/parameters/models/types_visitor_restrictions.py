from django.db import models

class TypesVisitorRestrictions(models.Model):
    class Meta:
        app_label = 'parameters'
        ordering = ['description']
        verbose_name = "05. Tipo de Restrição/Visitante"
        verbose_name_plural = "05. Tipos de Restrição/Visitantes"
        unique_together = ['description']
        db_table = 'parameters_typesvisitorrestrictions'

    description = models.CharField(max_length=100, unique=True, null=False, blank=False, verbose_name="Tipo de Restrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    def __str__(self):
        return self.description
