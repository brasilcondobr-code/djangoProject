from django.db import models
from .condominium_unit import CondominiumUnit

class RealEstateAgency(models.Model):
    class Meta:
        app_label = 'residents'
        ordering = ["condo_unit", "name", "created_at"]
        verbose_name = "07. Imobiliária"
        verbose_name_plural = "07. Imobiliárias"
        unique_together = (("condo_unit", "name"), ("condo_unit", "email"), ("condo_unit", "phone"))
        db_table = 'residents_realestateagency'

    
    condo_unit = models.ForeignKey(
        'residents.CondominiumUnit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='real_estate_units',
        verbose_name="Condomínio/Unidade"
    )
    name = models.CharField(max_length=200, verbose_name="Nome da Imobiliária")
    trade_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome Fantasia")
    cnpj = models.CharField(max_length=20, verbose_name="CNPJ")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    email = models.EmailField(verbose_name="E-mail")
    website = models.URLField(blank=True, verbose_name="Site")
    address = models.ForeignKey(
        'parameters.Addresses', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='agencies', verbose_name="Endereço"
    )
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Pessoa de contato")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

