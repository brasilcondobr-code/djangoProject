from django.db import models


class ChartofaccountsSubgroup(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '20. Subgrupo de Conta Contábil'
        verbose_name_plural = '20. Subgrupos de Contas Contábeis'
        ordering = ['main_group', 'description']
        db_table = 'parameters_chartofaccountssubgroup'

    code = models.CharField(max_length=50, unique=True, verbose_name='Código')
    main_group = models.ForeignKey(
        'ChartofaccountsMaingroup', on_delete=models.PROTECT,
        related_name='subgroups',
        verbose_name='Grupos Principais de Contas Contábeis',
    )
    description = models.CharField(max_length=100, unique=True, verbose_name='Descrição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    def __str__(self):
        return f'{self.code} - {self.description}'
