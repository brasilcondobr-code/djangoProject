from django.db import models
from .states import States

class Addresses(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = "04. Endereço"
        verbose_name_plural = "04. Endereços"
        ordering = ["country", 'state', 'city', 'street', 'number', 'complement', "is_active", "created_at"]
        unique_together = ['street', 'number', 'neighborhood', 'city', 'state', 'zip_code']
        db_table = 'parameters_addresses'

    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    zip_code = models.CharField(max_length=20, null=False, blank=False, verbose_name="CEP")
    street = models.CharField(max_length=255, null=False, blank=False, verbose_name="Logradouro")
    number = models.IntegerField(null=False, blank=False, verbose_name="Número")
    complement = models.CharField(max_length=255, null=True, blank=True, verbose_name="Complemento")
    neighborhood = models.CharField(max_length=255, null=True, blank=True, verbose_name="Bairro")
    city = models.CharField(max_length=100, null=False, blank=False, verbose_name="Município")
    state = models.ForeignKey(States, related_name="address", null=False, blank=False, verbose_name="UF", on_delete=models.CASCADE)
    country = models.CharField(max_length=100, null=False, blank=False, default="Brasil", verbose_name="País")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        address_line = f"{self.street}, {self.number}"
        if self.complement:
            address_line += f" - {self.complement}"
        return f"{address_line} | {self.neighborhood} | {self.city}/{self.state.abbreviation} | {self.zip_code}"
