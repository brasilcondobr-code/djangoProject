from django.db import models
from .types_collaborator import TypesCollaborator
from .condominium import Condominium

class Collaborator(models.Model):
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
    
    class Meta:
        app_label = 'condominium'
        verbose_name = "03. Colaborador"
        verbose_name_plural = "03. Colaboradores"
        ordering = ["name", "email", "phone_number", "created_at"]
        unique_together = [['name', 'cpf'], ['condominium', 'cpf']]
        db_table = 'condominium_collaborators'

    condominium = models.ForeignKey(Condominium, related_name="collaborators", null=False, blank=False, verbose_name="Condomínio", on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome", db_index=True)
    cpf = models.CharField(max_length=20, null=False, blank=False, verbose_name="CPF", unique=True)
    rg = models.CharField(max_length=20, null=False, blank=False, verbose_name="RG")
    email = models.EmailField(max_length=255, null=False, blank=False, verbose_name="Email", unique=True)
    phone_number = models.CharField(max_length=20, null=False, blank=False, verbose_name="Telefone")
    type_collaborator = models.ForeignKey(TypesCollaborator, related_name="Types_collaborators", null=True, blank=False, verbose_name="Tipo de Colaborador", on_delete=models.CASCADE)
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
        upload_to='certidoes/', 
        null=True, 
        blank=True, 
        verbose_name="Arquivo da certidão"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
