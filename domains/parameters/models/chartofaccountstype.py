from django.db import models


class Chartofaccountstype(models.Model):
    class NatureChoices(models.TextChoices):
        DEBIT = 'devedora', 'Devedora'
        CREDIT = 'credora', 'Credora'

    class Meta:
        app_label = 'parameters'
        verbose_name = '17. Tipo de Conta Contábil'
        verbose_name_plural = '17. Tipos de Contas Contábeis'
        ordering = ['code']
        db_table = 'parameters_chartofaccountstype'
        constraints = [
            models.UniqueConstraint(fields=['description', 'nature'], name='uq_chartofaccountstype_description_nature'),
        ]

    code = models.CharField(max_length=50, unique=True, verbose_name='Código do tipo')
    description = models.CharField(max_length=100, verbose_name='Descrição')
    nature = models.CharField(max_length=50, choices=NatureChoices.choices, verbose_name='Natureza contábil')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    def __str__(self):
        return f'{self.code} - {self.description}'
