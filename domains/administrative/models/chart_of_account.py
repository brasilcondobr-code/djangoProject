from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class ChartOfAccount(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = '09. Plano de Conta'
        verbose_name_plural = '09. Plano de Contas'
        ordering = ['condominium', 'account_code']
        db_table = 'administrative_chartofaccount'
        constraints = [
            models.UniqueConstraint(
                fields=['condominium', 'account_code'],
                name='uq_chart_account_condominium_code',
            ),
        ]
        indexes = [
            models.Index(fields=['condominium', 'account_code']),
            models.Index(fields=['condominium', 'status']),
            models.Index(fields=['condominium', 'account_level']),
            models.Index(fields=['condominium', 'parent_account']),
            models.Index(fields=['account_code']),
            models.Index(fields=['account_name']),
            models.Index(fields=['effective_start_date']),
            models.Index(fields=['effective_end_date']),
        ]

    condominium = models.ForeignKey(
        'condominium.Condominium', on_delete=models.CASCADE,
        related_name='chart_of_accounts',
        verbose_name='Condomínio',
    )
    account_code = models.CharField(
        max_length=20, verbose_name='Código da conta',
    )
    account_name = models.CharField(
        max_length=150, verbose_name='Nome da conta',
    )
    account_type = models.ForeignKey(
        'parameters.Chartofaccountstype', on_delete=models.PROTECT,
        related_name='chart_of_accounts',
        verbose_name='Tipo da conta',
    )
    account_level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='Nível hierárquico',
    )
    account_class = models.ForeignKey(
        'parameters.Accountingclasstypes', on_delete=models.PROTECT,
        related_name='chart_of_accounts',
        verbose_name='Classe contábil',
    )
    account_group = models.ForeignKey(
        'parameters.ChartofaccountsMaingroup', on_delete=models.PROTECT,
        related_name='chart_of_accounts',
        null=True, blank=True,
        verbose_name='Grupo principal',
    )
    account_subgroup = models.ForeignKey(
        'parameters.ChartofaccountsSubgroup', on_delete=models.PROTECT,
        related_name='chart_of_accounts',
        null=True, blank=True,
        verbose_name='Subgrupo',
    )
    parent_account = models.ForeignKey(
        'self', on_delete=models.PROTECT,
        related_name='child_accounts',
        null=True, blank=True,
        verbose_name='Conta-pai',
    )
    account_description = models.TextField(
        max_length=1000, blank=True,
        verbose_name='Descrição detalhada da conta',
    )
    external_reference = models.CharField(
        max_length=50, blank=True,
        verbose_name='Referência externa',
    )
    status = models.ForeignKey(
        'parameters.ChartofaccountsStatus', on_delete=models.PROTECT,
        related_name='chart_of_accounts',
        verbose_name='Situação da conta',
    )
    effective_start_date = models.DateField(
        verbose_name='Data inicial de vigência',
    )
    effective_end_date = models.DateField(
        null=True, blank=True,
        verbose_name='Data final de vigência',
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Conta padrão',
    )
    is_system_account = models.BooleanField(
        default=False,
        verbose_name='Conta do sistema',
    )
    can_be_archived = models.BooleanField(
        default=True,
        verbose_name='Permite arquivamento',
    )
    archive_reason = models.CharField(
        max_length=255, blank=True,
        verbose_name='Motivo do arquivamento',
    )
    replacement_account = models.ForeignKey(
        'self', on_delete=models.PROTECT,
        related_name='accounts_replaced',
        null=True, blank=True,
        verbose_name='Conta substituta',
    )
    version = models.CharField(
        max_length=20, blank=True, default='1.0',
        verbose_name='Versão do cadastro',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_chart_of_accounts',
        null=True, blank=True,
        verbose_name='Criado por',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='updated_chart_of_accounts',
        null=True, blank=True,
        verbose_name='Atualizado por',
    )
    approved_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Aprovado em',
    )
    approved_by = models.ForeignKey(
        'condominium.Collaborator', on_delete=models.PROTECT,
        related_name='approved_chart_of_accounts',
        null=True, blank=True,
        verbose_name='Aprovado por',
    )
    change_reason = models.CharField(
        max_length=500, blank=True,
        verbose_name='Motivo da alteração',
    )

    def __str__(self):
        return f'{self.account_code} - {self.account_name}'
