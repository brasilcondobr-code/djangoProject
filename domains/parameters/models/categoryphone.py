from django.db import models


class CategoryPhone(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '26. Categoria de Telefone'
        verbose_name_plural = '26. Categorias de Telefone'
        ordering = ['name']

    name = models.CharField(
        verbose_name='Nome',
        max_length=255,
        null=False,
        blank=False,
    )

    is_active = models.BooleanField(
        verbose_name='Ativo',
        default=True,
    )

    def __str__(self):
        return self.name or '26. Categoria de Telefone'
