from django.db import models

# Create your models here.
class BusinessSector(models.Model):
    description = models.CharField(max_length=100, verbose_name="Ramo de Atividade")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        ordering = ['description']
        verbose_name = "01. Ramo de Atividade"
        verbose_name_plural = "01. Ramos de Atividade"
        unique_together = ['description']

    def __str__(self):
        return self.description


class Entity(models.Model):
    RECEITA_STATUS_CHOICES = (
        ('Regular', 'Regular'),
        ('Suspenso', 'Suspenso'),
        ('Pendente de Regularização', 'Pendente de Regularização'),
        ('Cancelado', 'Cancelado'),
        ('Titular Falecido', 'Titular Falecido'),
        ('Nulo', 'Nulo'),
    )
    YES_NO_CHOICES = (
        ('Sim', 'Sim'),
        ('Não', 'Não'),
    )

    KIND_CHOICES = (
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    )
    
    SEX_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    )
    
    code = models.CharField(max_length=100, verbose_name="Código", unique=True)
    kind = models.CharField(max_length=2, choices=KIND_CHOICES, verbose_name="Tipo")
    business_sector = models.ForeignKey(BusinessSector, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ramo de Atividade")
    name = models.CharField(max_length=100, verbose_name="Nome da Entidade")
    trade_name = models.CharField(max_length=100, verbose_name="Nome Fantasia", blank=True, null=True) 
    cpf_cnpj = models.CharField(max_length=20, verbose_name="CPF/CNPJ", unique=True)
    rg_ie = models.CharField(max_length=20, verbose_name="RG/IE")
    municipal_registration = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Municipal")
    date_of_birth_opening = models.DateField(verbose_name="Data de Nascimento/Abertura", blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, null=True , verbose_name="Sexo")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    address = models.ForeignKey('parameters.Addresses', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Endereço")
    observations = models.TextField(verbose_name="Observações", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    situation = models.CharField(
        max_length=100,
        choices=RECEITA_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Situação Receita Federal"
    )
    regular = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        null=True,
        blank=True,
        verbose_name="CPF/CNPJ Regular"
    )
    death = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Óbito"
    )
    api_status = models.CharField(
        max_length=100,
        default='nulo',
        null=True,
        blank=True,
        editable=False,
        verbose_name="Status da API"
    )
    retorno_api = models.TextField(
        default='nulo',
        null=True,
        blank=True,
        editable=False,
        verbose_name='Retorno da API'
    )
    date_time_appointment = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
        editable=False,
        verbose_name='Data/hora da consulta'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        ordering = ['business_sector','name','cpf_cnpj']
        verbose_name = "02. Entidade"
        verbose_name_plural = "02. Entidades"
        unique_together = ['business_sector', 'cpf_cnpj']

    def __str__(self):
        return self.name
