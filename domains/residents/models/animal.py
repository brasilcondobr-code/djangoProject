from django.db import models
from .condominium_unit import CondominiumUnit

class Animal(models.Model):
    class Meta:
        app_label = 'residents'
        ordering = ["condo_unit", "name", "species", "created_at"]
        verbose_name = "05. Animal"
        verbose_name_plural = "05. Animais"
        unique_together = (("condo_unit", "name"), ("condo_unit", "species", "breed"))
        db_table = 'residents_animal'


    SPECIES_CHOICES = [
        ('dog', 'Cachorro'),
        ('cat', 'Gato'),
        ('bird', 'Pássaro'),
        ('other', 'Outro'),
    ]
    GENDER_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
        ('U', 'Desconhecido'),
    ]
    condo_unit = models.ForeignKey(CondominiumUnit, on_delete=models.CASCADE, related_name="animals", verbose_name="Condomínio/Unidade", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="Nome")
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES, default='dog', verbose_name="Espécie")
    breed = models.CharField(max_length=100, blank=True, verbose_name="Raça")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Idade")
    color = models.CharField(max_length=50, blank=True, verbose_name="Cor")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U', verbose_name="Sexo")
    photo = models.ImageField(upload_to='residents/animals/', null=True, blank=True, verbose_name="Foto")
    notes = models.TextField(blank=True, verbose_name="Notas")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

