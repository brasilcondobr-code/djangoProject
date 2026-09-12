from django.db import models
from domains.parameters.models.addresses import Addresses


class Bank(models.Model):
    compe = models.PositiveIntegerField(
        null=False, blank=False, unique=True, verbose_name="Cod. Banco",
    )
    bank_name = models.CharField(
        max_length=255, null=False, blank=False, verbose_name="Nome Banco",
    )
    iban = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="IBAN",
    )
    bank_address = models.ForeignKey(
        Addresses, related_name='bank', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Endereço do Banco",
    )
    is_active = models.BooleanField(default=False, verbose_name="Ativo")

    # Gerente
    full_name_manager = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="Nome do Gerente",
    )
    phone1_manager = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Telefone 1 Gerente",
    )
    phone2_manager = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Telefone 2 Gerente",
    )
    phone3_manager = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Telefone 3 Gerente",
    )
    email_manager = models.EmailField(
        null=True, blank=True, verbose_name="Email Gerente",
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="Atualizado em")

    class Meta:
        app_label = 'administrative'
        verbose_name = "01. Banco"
        verbose_name_plural = "01. Bancos"

    def __str__(self):
        return self.bank_name
