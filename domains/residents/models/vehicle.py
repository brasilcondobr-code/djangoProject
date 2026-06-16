from django.db import models
from .condominium_unit import CondominiumUnit

class Vehicle(models.Model):
    class Meta:
        app_label = 'residents'
        ordering = ["condo_unit", "vehicle_type", "license_plate", "created_at"]
        verbose_name = "03. Veículo"
        verbose_name_plural = "03. Veículos"
        unique_together = (("condo_unit", "license_plate"), ("condo_unit", "vehicle_type", "model", "year"))
        db_table = 'residents_vehicle'


    VEHICLE_TYPE_CHOICES = [
        ('car', 'Carro'),
        ('motorcycle', 'Moto'),
        ('truck', 'Caminhão'),
        ('pickup truck', 'Caminhonete'),
        ('trailer', 'Reboque'),
        ('mpped', 'Ciclomotor'),
        ('bicycle', 'Bicicleta'),
        ('other', 'Outro'),
    ]
    condo_unit = models.ForeignKey(CondominiumUnit, on_delete=models.CASCADE, null=True, blank=True, related_name="vehicles", verbose_name="Condomínio/Unidade")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='car', verbose_name="Tipo")
    license_plate = models.CharField(max_length=8, verbose_name="Placa")
    brand = models.CharField(max_length=50, blank=True, verbose_name="Marca")
    model = models.CharField(max_length=100, blank=True, verbose_name="Modelo")
    color = models.CharField(max_length=30, blank=True, verbose_name="Cor")
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Ano")
    garage_space = models.CharField(max_length=50, blank=True, verbose_name="Vaga de garagem")
    photo = models.ImageField(upload_to='residents/vehicles/', null=True, blank=True, verbose_name="Foto")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.license_plate

