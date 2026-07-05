from django.db import models
 
class MeterType(models.Model):
    description = models.CharField(max_length=255, verbose_name="Descrição", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
 
    class Meta:
        app_label = 'parameters'
        verbose_name = "09. Tipo de Medidor"
        verbose_name_plural = "09. Tipos de Medidores"
        ordering = ["description"]
 
    def __str__(self):
        return self.description

