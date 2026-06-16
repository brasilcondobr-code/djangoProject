from django.db import models
from .condominium_unit import CondominiumUnit

class Emergency(models.Model):
    class Meta:
        app_label = 'residents'
        ordering = ["condo_unit", "type", "occurred_at", "created_at"]
        verbose_name = "04. Emergência"
        verbose_name_plural = "04. Emergências"
        unique_together = (("condo_unit", "type", "occurred_at"), ("condo_unit", "description", "occurred_at"))
        db_table = 'residents_emergency'


    EMERGENCY_CHOICES = [
        ('fire', 'Incêndio'),
        ('medical', 'Emergência Médica'),
        ('security', 'Segurança'),
        ('leaks', 'Vazamentos'),
        ('power', 'Falta de energia'),
        ('personal accidents', 'Acidentes pessoais'),
        ('structural damage', 'Danos estruturais'),
        ('conflicts', 'Conflitos'),
        ('other', 'Outros'),
    ]
    condo_unit = models.ForeignKey(CondominiumUnit, on_delete=models.CASCADE, null=True, blank=True, related_name='emergencies', verbose_name="Condomínio/Unidade")
    type = models.CharField(max_length=20, choices=EMERGENCY_CHOICES, default='other', verbose_name="Tipo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    occurred_at = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} | {self.condo_unit}".strip()

