from django.db import models
from domains.administrative.models.bank import Bank
from domains.condominium.models.condominium import Condominium
from domains.parameters.models.bank_account_type import BankAccountType


class BankAccount(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = '02. Conta Bancária'
        verbose_name_plural = '02. Contas Bancárias'
        ordering = ['account_name']
        db_table = 'administrative_bankaccount'
        constraints = [
            models.UniqueConstraint(
                fields=['bank', 'condominium', 'account_type', 'agency'],
                name='uq_bank_account_bank_condominium_type_agency',
            ),
            models.UniqueConstraint(
                fields=['bank', 'agency', 'account_number'],
                name='uq_bank_account_bank_agency_number',
            ),
        ]

        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['bank', 'condominium']),
        ]

    bank = models.ForeignKey(
        Bank,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name='Banco',
        related_name='bank_accounts',
    )

    condominium = models.ForeignKey(
        Condominium,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name='Condomínio',
        related_name='bank_accounts',
    )

    account_type = models.ForeignKey(
        BankAccountType,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name='Tipo de Conta',
        related_name='bank_accounts',
    )

    initial_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Saldo Inicial',
    )

    initial_balance_date = models.DateField(
        null=False,
        blank=False,
        verbose_name='Data do Saldo Inicial',
    )

    account_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name='Nome da Conta',
    )

    agency = models.CharField(
        max_length=6,
        null=False,
        blank=False,
        verbose_name='Agência',
    )

    account_number = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        verbose_name='Número da Conta',
    )

    account_digit = models.CharField(
        max_length=3,
        null=False,
        blank=False,
        default='',
        verbose_name='Dígito da Conta',
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name='Ativo',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    def __str__(self):
        return f"{self.account_name} - {self.bank.bank_name}"
