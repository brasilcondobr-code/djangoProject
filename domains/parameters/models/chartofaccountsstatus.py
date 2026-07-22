from django.db import models


class ChartofaccountsStatus(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '21. Situação de Conta Contábil'
        verbose_name_plural = '21. Situações de Contas Contábeis'
        ordering = ['description']
        db_table = 'parameters_chartofaccountsstatus'

    description = models.CharField(max_length=50, unique=True, verbose_name='Descrição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    def __str__(self):
        return self.description
