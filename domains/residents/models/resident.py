from django.db import models
from .condominium_unit import CondominiumUnit

class SexChoices(models.TextChoices):
    MALE = 'M', 'Masculino'
    FEMALE = 'F', 'Feminino'

class Resident(models.Model):
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
    
    unit = models.ForeignKey(CondominiumUnit, on_delete=models.CASCADE, related_name="residents", verbose_name="Unidade")
    type_of_resident = models.ForeignKey(
        'parameters.ResidentType',
        related_name='resident',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Tipo de morador'
    )
    name = models.CharField(max_length=250, verbose_name="Nome")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    cpf = models.CharField(max_length=14, verbose_name="CPF")
    rg = models.CharField(max_length=20, verbose_name="RG")
    sex = models.CharField(max_length=1, choices=SexChoices.choices, verbose_name="Sexo")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Data de nascimento")
    profission = models.CharField(max_length=100, blank=True, verbose_name="Profissão")
    is_primary = models.BooleanField(default=False, verbose_name="Principal")
    is_resident = models.BooleanField(default=True, verbose_name="É residente")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    photo = models.ImageField(upload_to='residents/photos/', null=True, blank=True, verbose_name="Foto")
    
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
        verbose_name="CPF Regular"
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
    certificate_presentation_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data de apresentação da certidão"
    )
    certificate_validity = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Validade da certidão"
    )
    observations_certificate = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Observações da certidão"
    )
    certificate_file = models.FileField(
        upload_to='residents/certidoes/', 
        null=True, 
        blank=True, 
        verbose_name="Arquivo da certidão"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        app_label = 'residents'
        ordering = ["unit", "name", "created_at"]
        verbose_name = "02. Morador"
        verbose_name_plural = "02. Moradores"
        unique_together = (("unit", "name"), ("unit", "cpf"), ("unit", "rg"))
        db_table = 'residents_resident'

    
    def __str__(self):
        try:
            unit_str = str(self.unit) if self.unit else "Sem Unidade"
        except Exception:
            unit_str = "Sem Unidade"
        return f"{self.name} | {unit_str}".strip()
