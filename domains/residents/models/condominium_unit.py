from django.db import models

class FloorChoices(models.TextChoices):
    INFERIOR = "inferior", "Inferior"
    TERREO = "terreo", "Térreo"
    ONE = "1", "1° andar"
    TWO = "2", "2° andar"
    THREE = "3", "3° andar"
    FOUR = "4", "4° andar"
    FIVE = "5", "5° andar"
    TERRACE = "terraco", "Terraço"

class UnitTypeChoices(models.TextChoices):
    APARTMENT = "apartment", "Apartamento"
    HOUSE = "house", "Casa"
    COMMERCIAL = "commercial", "Comercial"
    OFFICE = "office", "Sala Comercial"
    STORE = "store", "Loja"

class YesNo(models.TextChoices):
    YES = "S", "Sim"
    NO = "N", "Não"

class UnitStatus(models.TextChoices):
    AVAILABLE = "available", "Disponível"
    OCCUPIED = "occupied", "Ocupado"
    MAINTENANCE = "maintenance", "Manutenção"
    RESERVED = "reserved", "Reservado"

class CondominiumUnit(models.Model):
    class Meta:
        app_label = 'residents'
        ordering = ["tower", "unit_number", "floor", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["tower", "unit_number"], name="unique_unit_per_tower")
        ]
        verbose_name = "01. Unidade"
        verbose_name_plural = "01. Unidades"
        unique_together = (("tower", "unit_number"),)
        db_table = 'residents_condominiumunit'

from django.db import models

class FloorChoices(models.TextChoices):
    INFERIOR = "inferior", "Inferior"
    TERREO = "terreo", "Térreo"
    ONE = "1", "1° andar"
    TWO = "2", "2° andar"
    THREE = "3", "3° andar"
    FOUR = "4", "4° andar"
    FIVE = "5", "5° andar"
    TERRACE = "terraco", "Terraço"

class UnitTypeChoices(models.TextChoices):
    APARTMENT = "apartment", "Apartamento"
    HOUSE = "house", "Casa"
    COMMERCIAL = "commercial", "Comercial"
    OFFICE = "office", "Sala Comercial"
    STORE = "store", "Loja"

class YesNo(models.TextChoices):
    YES = "S", "Sim"
    NO = "N", "Não"

class UnitStatus(models.TextChoices):
    AVAILABLE = "available", "Disponível"
    OCCUPIED = "occupied", "Ocupado"
    MAINTENANCE = "maintenance", "Manutenção"
    RESERVED = "reserved", "Reservado"

class CondominiumUnit(models.Model):
    class Meta:
        app_label = 'residents'
        ordering = ["tower", "unit_number", "floor", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["tower", "unit_number"], name="unique_unit_per_tower")
        ]
        verbose_name = "01. Unidade"
        verbose_name_plural = "01. Unidades"
        unique_together = (("tower", "unit_number"),)
        db_table = 'residents_condominiumunit'

    condominium = models.ForeignKey(
        'condominium.Condominium',
        on_delete=models.CASCADE,
        related_name="units",
        verbose_name="Condomínio"
    )
    tower = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Bloco / Torre"
    )
    unit_number = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="Número da unidade"
    )
    floor = models.CharField(
        max_length=20,
        choices=FloorChoices.choices,
        verbose_name="Pavimento"
    )
    identification = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Identificação"
    )
    unit_type = models.CharField(
        default=UnitTypeChoices.APARTMENT,
        max_length=20,
        choices=UnitTypeChoices.choices,
        verbose_name="Tipo"
    )
    bedrooms = models.PositiveIntegerField(default=2, verbose_name="Número de quartos")
    bathrooms = models.PositiveIntegerField(default=1, verbose_name="Número de banheiros")
    suites = models.PositiveIntegerField(default=0, verbose_name="Número de suítes")
    garage_spaces = models.PositiveIntegerField(default=1, verbose_name="Número de vagas de garagem")
    area_total = models.DecimalField(default=60.00, max_digits=10, decimal_places=2, verbose_name="Área total")
    status = models.CharField(
        max_length=20,
        choices=UnitStatus.choices,
        default=UnitStatus.AVAILABLE,
        verbose_name="Status"
    )
    for_sale = models.BooleanField(default=False, verbose_name="Para venda")
    for_rent = models.BooleanField(default=False, verbose_name="Para alugel")
    sale_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Preço de venda")
    rent_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Preço de alugel")
    notes = models.TextField(blank=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        condominium_name = getattr(self.condominium, "name", "")
        if condominium_name:
            condominium_name = f"{condominium_name}"
            
        tower_name = ""
        if hasattr(self, "tower") and getattr(self, "tower"):
            tower_name = str(self.tower)
        elif hasattr(self, "structure") and getattr(self, "structure"):
            tower_name = str(self.unit_number) if hasattr(self, "unit_number") and getattr(self, "unit_number") else ""
        unit = getattr(self, "unit_number", "")
        if tower_name:
            return f" {condominium_name} - {tower_name} - {unit}".strip()
        return f"-01. Unidade {unit}".strip()
    tower = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Bloco / Torre"
    )
    unit_number = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="Número da unidade"
    )
    floor = models.CharField(
        max_length=20,
        choices=FloorChoices.choices,
        verbose_name="Pavimento"
    )
    identification = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Identificação"
    )
    unit_type = models.CharField(
        default=UnitTypeChoices.APARTMENT,
        max_length=20,
        choices=UnitTypeChoices.choices,
        verbose_name="Tipo"
    )
    bedrooms = models.PositiveIntegerField(default=2, verbose_name="Número de quartos")
    bathrooms = models.PositiveIntegerField(default=1, verbose_name="Número de banheiros")
    suites = models.PositiveIntegerField(default=0, verbose_name="Número de suítes")
    garage_spaces = models.PositiveIntegerField(default=1, verbose_name="Número de vagas de garagem")
    area_total = models.DecimalField(default=60.00, max_digits=10, decimal_places=2, verbose_name="Área total")
    status = models.CharField(
        max_length=20,
        choices=UnitStatus.choices,
        default=UnitStatus.AVAILABLE,
        verbose_name="Status"
    )
    for_sale = models.BooleanField(default=False, verbose_name="Para venda")
    for_rent = models.BooleanField(default=False, verbose_name="Para aluguel")
    sale_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Preço de venda")
    rent_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Preço de aluguel")
    notes = models.TextField(blank=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        condominium_name = getattr(self.condominium, "name", "")
        if condominium_name:
            condominium_name = f"{condominium_name}"
            
        tower_name = ""
        if hasattr(self, "tower") and getattr(self, "tower"):
            tower_name = str(self.tower)
        elif hasattr(self, "structure") and getattr(self, "structure"):
            tower_name = str(self.unit_number) if hasattr(self, "unit_number") and getattr(self, "unit_number") else ""
        unit = getattr(self, "unit_number", "")
        if tower_name:
            return f" {condominium_name} - {tower_name} - {unit}".strip()
        return f"-01. Unidade {unit}".strip()
