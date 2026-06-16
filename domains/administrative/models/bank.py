from django.db import models
from domains.parameters.models.addresses import Addresses
from domains.condominium.models.condominium import Condominium

ACCOUNT_TYPE_CHOICES = (
    ('checking_account', 'Conta Corrente'),
    ('savings_account', 'Conta Poupança'),
    ('university_account', 'Conta Universitária'),
    ('digital_account', 'Conta Digital'),
    ('salary_account', 'Conta-Salário'),
    ('joint_account', 'Conta Conjunta'),
    ('business_account', 'Conta Empresarial'),
    ('international_account', 'Conta Internacional'),
    ('investment_account', 'Conta Investimento'),
)

class Bank(models.Model):
    compe = models.PositiveIntegerField(null=False, blank=False, verbose_name="Cod. Banco")
    bank_name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome Banco")
    account_type = models.CharField(max_length=50, null=False, blank=False, choices=ACCOUNT_TYPE_CHOICES, verbose_name="Tipo de Conta")
    initial_balance = models.DecimalField(max_digits=14, decimal_places=2, null=False, blank=False, verbose_name="Saldo Inicial")
    initial_balance_date = models.DateField(null=True, blank=True, verbose_name="Data Saldo Inicial")
    account_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nome da Conta")
    iban = models.CharField(max_length=30, null=True, blank=True, verbose_name="IBAN")
    agency = models.CharField(max_length=10, null=False, blank=False, verbose_name="Agência")
    account_number = models.CharField(max_length=20, null=False, blank=False, verbose_name="Número da Conta")
    account_digit = models.CharField(max_length=2, null=False, blank=False, verbose_name="Dígito da Conta")
    bank_address = models.ForeignKey(Addresses, related_name='bank', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Endereço do Banco")
    is_active = models.BooleanField(default=False, verbose_name="Ativo")
    
    # Beneficiário
    condominium = models.ForeignKey(Condominium, related_name='bank', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Condomínio Beneficiário")
    
    # Sacado Avalista
    full_name_drawn = models.CharField(max_length=250, null=False, blank=False, verbose_name="Nome Completo Sacado")
    cpf_drawn = models.CharField(max_length=14, null=False, blank=False, verbose_name="CPF Sacado")
    rg_drawn = models.CharField(max_length=20, null=False, blank=False, verbose_name="RG Sacado")
    phone_drawn = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Sacado")
    email_drawn = models.EmailField(null=False, blank=False, verbose_name="Email Sacado")
    addresses_drawn = models.ForeignKey(Addresses, related_name='drawn_address', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Endereço Sacado")
    
    # Gerente
    full_name_manager = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nome do Gerente")
    phone1_manager = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone 1 Gerente")
    phone2_manager = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone 2 Gerente")
    phone3_manager = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone 3 Gerente")
    email_manager = models.EmailField(null=True, blank=True, verbose_name="Email Gerente")
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="Atualizado em")

    class Meta:
        app_label = 'administrative'
        verbose_name = "01. Banco"
        verbose_name_plural = "01. Bancos"
        unique_together = [
            ('compe', 'account_type', 'agency', 'account_number'),
            ('compe', 'agency', 'account_number', 'cpf_drawn'),
        ]

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"
