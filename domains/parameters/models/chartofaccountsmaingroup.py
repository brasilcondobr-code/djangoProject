from django.db import models


class ChartofaccountsMaingroup(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '19. Grupo Principal de Conta Contábil'
        verbose_name_plural = '19. Grupos Principais de Contas Contábeis'
        ordering = ['account_class', 'description']
        db_table = 'parameters_chartofaccountsmaingroup'

    code = models.CharField(max_length=50, unique=True, verbose_name='Código')
    account_class = models.ForeignKey(
        'Accountingclasstypes', on_delete=models.PROTECT,
        related_name='main_groups',
        verbose_name='Classes Contábeis',
    )
    description = models.CharField(max_length=100, unique=True, verbose_name='Descrição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    def __str__(self):
        return f'{self.code} - {self.description}'
