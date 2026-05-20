from django.db import models
from parameters.models import Addresses, TypesCondominium, StructionCondominium

# Create your models here.

class Condominium(models.Model):
    code = models.CharField(max_length=100, verbose_name="Código", unique=True)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome")
    cnpj = models.CharField(max_length=20, null=False, blank=False, verbose_name="CNPJ", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    state_registration = models.CharField(max_length=20, verbose_name="Inscrição Estadual")
    municipal_registration = models.CharField(max_length=20, verbose_name="Inscrição Municipal")
    type_condominium = models.ForeignKey(TypesCondominium, related_name="condominium", null=False, blank=False, verbose_name="Tipo de Condomínio",
                                      on_delete=models.CASCADE)
    struction_condominium = models.ForeignKey(StructionCondominium, related_name="condominium", null=True, blank=False, verbose_name="Estrutura do Condomínio",
                                      on_delete=models.CASCADE)
    address = models.ForeignKey(Addresses, related_name="condominium", null=False, blank=False, verbose_name="Endereço",
                                on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "01. Condomínio"
        verbose_name_plural = "01. Condomínios"
        ordering = ["name", "code", "cnpj", "is_active", "created_at"]
        ##unique_together = [['cnpj'], ['code']]

    def __str__(self):
        return self.name
    

class Types_collaborators(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name="Tipo de Colaborador")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "02. Tipo de Colaborador"
        verbose_name_plural = "02. Tipos de Colaboradores"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
    
    def __str__(self):
        return self.name


class Collaborators(models.Model):
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

    condominium = models.ForeignKey(Condominium, related_name="collaborators", null=False, blank=False, verbose_name="Condomínio", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome")
    cpf = models.CharField(max_length=20, null=False, blank=False, verbose_name="CPF", unique=True)
    rg = models.CharField(max_length=20, null=False, blank=False, verbose_name="RG")
    email = models.EmailField(max_length=255, null=False, blank=False, verbose_name="Email", unique=True)
    phone_number = models.CharField(max_length=20, null=False, blank=False, verbose_name="Telefone")
    type_collaborator = models.ForeignKey(Types_collaborators, related_name="Types_collaborators", null=True, blank=False, verbose_name="Tipo de Colaborador", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    photo = models.ImageField(upload_to='condominium/collaborators/', null=True, blank=True, verbose_name="Foto")
    observations = models.TextField(null=True, blank=True, verbose_name="Observações")
    
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
        verbose_name="Retorno da API"
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
        verbose_name="Observações"
    )
    certificate_file = models.FileField(
        upload_to='certidoes/',
        null=True,
        blank=True,
        verbose_name="Arquivo da certidão"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "03. Colaborador"
        verbose_name_plural = "03. Colaboradores"
        ordering = ["name", "email", "phone_number", "created_at"]
        unique_together = [['name', 'cpf'], ['condominium', 'cpf']]

    def __str__(self):
        return self.name


class DocumentCondominium(models.Model):
    condominium = models.ForeignKey(Condominium, related_name="documents", null=False, blank=False, verbose_name="Condomínio", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome do Documento")
    file = models.FileField(upload_to='condominium/documents/', null=False, blank=False, verbose_name="Arquivo do Documento")
    observations = models.TextField(null=True, blank=True, verbose_name="Observações")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "04. Documento do Condomínio"
        verbose_name_plural = "04. Documentos do Condomínio"
        ordering = ["name", "created_at"]

    def __str__(self):
        return self.name