from django.db import models
from parameters.models import Addresses
from condominium.models import Condominium

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
        verbose_name = "1. Banco"
        verbose_name_plural = "1. Bancos"
        unique_together = [
            ('compe', 'account_type', 'agency', 'account_number'),
            ('compe', 'agency', 'account_number', 'cpf_drawn'),
        ]

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

class Circular(models.Model):
    class Meta:
        verbose_name = "2. Circular"
        verbose_name_plural = "2. Circulares"

    def __str__(self):
        return "2. Circulares"

class Contract(models.Model):
    class Meta:
        verbose_name = "3. Contrato"
        verbose_name_plural = "3. Contratos"

    def __str__(self):
        return "3. Contratos"

class Infraction(models.Model):
    class Meta:
        verbose_name = "4. Infração"
        verbose_name_plural = "4. Infrações"

    def __str__(self):
        return "4. Infrações"

class Meter(models.Model):
    class Meta:
        verbose_name = "5. Medidor"
        verbose_name_plural = "5. Medidores"

    def __str__(self):
        return "5. Medidores"

class Notification(models.Model):
    class Meta:
        verbose_name = "6. Notificação"
        verbose_name_plural = "6. Notificações"

    def __str__(self):
        return "6. Notificações"

class Patrimony(models.Model):
    class Meta:
        verbose_name = "7. Patrimônio"
        verbose_name_plural = "7. Patrimônios"

    def __str__(self):
        return "7. Patrimônios"

class BudgetForecast(models.Model):
    class Meta:
        verbose_name = "8. Previsão Orçamentária"
        verbose_name_plural = "8. Previsões Orçamentárias"

    def __str__(self):
        return "8. Previsões Orçamentárias"

class ChartOfAccount(models.Model):
    class Meta:
        verbose_name = "9. Plano de Conta"
        verbose_name_plural = "9. Plano de Contas"

    def __str__(self):
        return "9. Plano de Contas"

class Project(models.Model):
    class Meta:
        verbose_name = "10. Projeto"
        verbose_name_plural = "10. Projetos"

    def __str__(self):
        return "10. Projetos"

class Task(models.Model):
    class Meta:
        verbose_name = "11. Tarefa"
        verbose_name_plural = "11. Tarefas"

    def __str__(self):
        return "11. Tarefas"


class VirtualAssembly(models.Model):
    class Meta:
        verbose_name = "12. Assembleia Virtual"
        verbose_name_plural = "12. Assembleias Virtuais"

    def __str__(self):
        return "12. Assembleias Virtuais"
