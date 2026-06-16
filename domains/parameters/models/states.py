from django.db import models

class States(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = "03. Estado"
        verbose_name_plural = "03. Estados"
        ordering = ["abbreviation", "name", "region"]
        unique_together = ['name', 'abbreviation']
        db_table = 'parameters_states'

    name = models.CharField(max_length=100, unique=True, verbose_name="Estado")
    abbreviation = models.CharField(max_length=2, unique=True, verbose_name="UF")
    capital = models.CharField(max_length=100, verbose_name="Capital", null=True, blank=False)
    REGION_CHOICES = [
        ('Região Norte', 'Região Norte'),
        ('Região Nordeste', 'Região Nordeste'),
        ('Região Centro-Oeste', 'Região Centro-Oeste'),
        ('Região Sudeste', 'Região Sudeste'),
        ('Região Sul', 'Região Sul'),
    ]
    region = models.CharField(max_length=100, verbose_name="Região", choices=REGION_CHOICES, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"
