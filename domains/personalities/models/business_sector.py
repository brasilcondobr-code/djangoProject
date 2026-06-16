from django.db import models

class BusinessSector(models.Model):
    class Meta:
        app_label = 'personalities'
        ordering = ['description']
        verbose_name = "01. Ramo de Atividade"
        verbose_name_plural = "01. Ramos de Atividade"
        unique_together = ['description']
        db_table = 'personalities_businesssector'

    description = models.CharField(max_length=100, verbose_name="Ramo de Atividade")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    def __str__(self):
        return self.description
