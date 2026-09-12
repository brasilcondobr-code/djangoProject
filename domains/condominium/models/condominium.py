from django.db import models
from domains.parameters.models import Addresses, TypesCondominium, StructionCondominium

class Condominium(models.Model):
    class Meta:
        app_label = 'condominium'
        verbose_name = "01. Condomínio"
        verbose_name_plural = "01. Condomínios"
        ordering = ["name", "code", "cnpj", "is_active", "created_at"]
        db_table = 'condominium_condominium'

    code = models.CharField(max_length=100, verbose_name="Código", unique=True)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome", db_index=True)
    cnpj = models.CharField(max_length=20, null=False, blank=False, verbose_name="CNPJ", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo", db_index=True)
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
    
    def __str__(self):
        return self.name


