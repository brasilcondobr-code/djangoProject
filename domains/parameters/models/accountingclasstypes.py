from django.db import models


class Accountingclasstypes(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '18. Classe Contábil'
        verbose_name_plural = '18. Classes Contábeis'
        ordering = ['code']
        db_table = 'parameters_accountingclasstypes'

    code = models.CharField(max_length=50, unique=True, verbose_name='Código da classe')
    description = models.CharField(max_length=100, unique=True, verbose_name='Descrição')
    account_type = models.ForeignKey(
        'Chartofaccountstype', on_delete=models.PROTECT,
        related_name='accounting_classes',
        verbose_name='Tipo de conta contábil',
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    def __str__(self):
        return f'{self.code} - {self.description} - {self.account_type}'
