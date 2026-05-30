from django.db import models
from .condominium_unit import CondominiumUnit
from .resident import Resident

class Visitor(models.Model):
    condo_unit = models.ForeignKey(CondominiumUnit, on_delete=models.CASCADE, null=True, blank=True, related_name="visitors", verbose_name="Condomínio/Unidade")
    name = models.CharField(max_length=250, verbose_name="Nome")
    cpf = models.CharField(max_length=14, verbose_name="CPF")
    rg = models.CharField(max_length=20, verbose_name="RG")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    purpose = models.CharField(max_length=255, blank=True, verbose_name="Propósito da visita")
    photo = models.ImageField(upload_to='residents/visitors/', null=True, blank=True, verbose_name="Foto")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    situation = models.CharField(
        max_length=100,
        choices=Resident.RECEITA_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Situação Receita Federal"
    )
    regular = models.CharField(
        max_length=3,
        choices=Resident.YES_NO_CHOICES,
        null=True,
        blank=True,
        verbose_name="CPF Regular"
    )
    death = models.CharField(
        max_length=3,
        choices=Resident.YES_NO_CHOICES,
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
    types_visitor_restriction = models.ForeignKey(
        'parameters.TypesVisitorRestrictions', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Tipos de Restrição"
    )
    restrictionVisitor_presentation_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data de apresentação"
    )
    restrictionVisitor_validity_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data de validade"
    )
    restrictionVisitor_observations = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Observações"
    )
    restrictionVisitor_file = models.FileField(
        upload_to='residents/restrictions/', 
        null=True, 
        blank=True, 
        verbose_name="Arquivo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'residents'
        ordering = ["condo_unit", "name", "created_at"]
        verbose_name = "06. Visitante"
        verbose_name_plural = "06. Visitantes"
        unique_together = (("condo_unit", "name"), ("condo_unit", "cpf"), ("condo_unit", "rg"))
        db_table = 'residents_visitor'

    
    def __str__(self):
        return f"{self.name} | {self.condo_unit}".strip()

