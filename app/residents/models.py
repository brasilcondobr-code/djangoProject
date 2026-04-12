from django.db import models
from condominium.models import Condominium


# Create your models here.
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

class SexChoices(models.TextChoices):
    MALE = 'M', 'Masculino'
    FEMALE = 'F', 'Feminino'

class UnitStatus(models.TextChoices):
    AVAILABLE = "available", "Disponível"
    OCCUPIED = "occupied", "Ocupado"
    MAINTENANCE = "maintenance", "Manutenção"
    RESERVED = "reserved", "Reservado"

class CondominiumUnit(models.Model):
    condominium = models.ForeignKey(
        Condominium,
        on_delete=models.CASCADE,
        related_name="units",
        verbose_name="Condomínio"
    )

    tower = models.CharField(
        max_length=20,
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
    area_total = models.DecimalField(default=60 ,max_digits=10, decimal_places=2, verbose_name="Área total")

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

    class Meta:
        ordering = ["unit_number"]
        constraints = [
            models.UniqueConstraint(fields=["tower", "unit_number"], name="unique_unit_per_tower")
        ]
        verbose_name = "1. Unidade"
        verbose_name_plural = "1. Unidades"
    
    def __str__(self):
        tower_name = ""
        if hasattr(self, "tower") and getattr(self, "tower"):
            tower_name = str(self.tower)
        # senão tenta o campo antigo/referência 'structure'
        elif hasattr(self, "structure") and getattr(self, "structure"):
            try:
                tower_name = str(self.structure)
            except Exception:
                tower_name = getattr(self.structure, "name", "")
        unit = getattr(self, "unit_number", "")
        if tower_name:
            return f"{tower_name} - {unit}".strip()
        return f"Unidade {unit}".strip()
    

class Resident(models.Model):
    unit = models.ForeignKey(CondominiumUnit, on_delete=models.CASCADE, related_name="residents", verbose_name="Unidade")
    name = models.CharField(max_length=250, verbose_name="Nome")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    cpf = models.CharField(max_length=14, blank=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, blank=True, verbose_name="RG")
    sex = models.CharField(max_length=1, choices=SexChoices.choices, verbose_name="Sexo")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Data de nascimento")
    profission = models.CharField(max_length=100, blank=True, verbose_name="Profissão")
    is_primary = models.BooleanField(default=False, verbose_name="Principal")
    is_resident = models.BooleanField(default=True, verbose_name="É residente")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "2. Morador"
        verbose_name_plural = "2. Moradores"

    def __str__(self):
        return f"{self.name} | {self.unit}".strip()


class Visitor(models.Model):
    condo_unit = models.ForeignKey('residents.CondominiumUnit', on_delete=models.CASCADE, null=True, blank=True, related_name="visitors", verbose_name="Unidade/Condomínio")
    name = models.CharField(max_length=250, verbose_name="Nome")
    cpf = models.CharField(max_length=14, blank=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, blank=True, verbose_name="RG")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    visit_date = models.DateTimeField(auto_now_add=True, verbose_name="Data da visita")
    purpose = models.CharField(max_length=255, blank=True, verbose_name="Propósito da visita")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "6. Visitante"
        verbose_name_plural = "6. Visitantes"

    def __str__(self):
        ## return f"{self.name} | {self.host}".strip()
        
        visitor_name = ""
        if hasattr(self, "first_name") and getattr(self, "first_name"):
            visitor_name = self.first_name
        if hasattr(self, "last_name") and getattr(self, "last_name"):
            visitor_name = (visitor_name + " " + self.last_name).strip() if visitor_name else self.last_name
        host_name = ""
        if hasattr(self, "host") and self.host:
            # Tenta obter o nome do host de Resident, se disponível
            if hasattr(self.host, "name") and self.host.name:
                host_name = self.host.name
            elif hasattr(self.host, "first_name") or hasattr(self.host, "last_name"):
                parts = []
                if getattr(self.host, "first_name", ""):
                    parts.append(self.host.first_name)
                if getattr(self.host, "last_name", ""):
                    parts.append(self.host.last_name)
                host_name = " ".join(parts).strip()

        if visitor_name and host_name:
            return f"{visitor_name} | {host_name}".strip()
        if visitor_name:
            return visitor_name.strip()
        if host_name:
            return host_name.strip()
        return super().__str__()
        
              

class RealEstateAgency(models.Model):
    condo_unit = models.ForeignKey(
        'residents.CondominiumUnit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='real_estate_units',
        verbose_name="Unidade/Condomínio"
    )
    name = models.CharField(max_length=200, verbose_name="Nome da Imobiliária")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    website = models.URLField(blank=True, verbose_name="Site")
    address = models.ForeignKey(
        'condominium.Addresses', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='agencies', verbose_name="Endereço"
    )
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Pessoa de contato")
    active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "7. Imobiliária"
        verbose_name_plural = "7. Imobiliárias"

    def __str__(self):
        return self.name

class Emergency(models.Model):
    EMERGENCY_CHOICES = [
        ('fire', 'Incêndio'),
        ('medical', 'Emergência Médica'),
        ('security', 'Segurança'),
        ('leaks', 'Vazamentos'),
        ['power', 'Falta de energia'],
        ['personal accidents', 'Acidentes pessoais'],
        ['structural damage', 'Danos estruturais'],
        ['conflicts', 'Conflitos'],
        ('other', 'Outros'),
    ]
    condo_unit = models.ForeignKey('residents.CondominiumUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='emergencies', verbose_name="Unidade/Condomínio")
    type = models.CharField(max_length=20, choices=EMERGENCY_CHOICES, default='other', verbose_name="Tipo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    occurred_at = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "4. Emergência"
        verbose_name_plural = "4. Emergências"

    def __str__(self):
        return f"{self.get_type_display()} em {self.occurred_at}"

class Vehicle(models.Model):
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
    condo_unit = models.ForeignKey('residents.CondominiumUnit', on_delete=models.CASCADE, null=True, blank=True, related_name="vehicles", verbose_name="Unidade/Condomínio")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='car', verbose_name="Tipo")
    license_plate = models.CharField(max_length=20, verbose_name="Placa")
    brand = models.CharField(max_length=50, blank=True, verbose_name="Marca")
    model = models.CharField(max_length=100, blank=True, verbose_name="Modelo")
    color = models.CharField(max_length=30, blank=True, verbose_name="Cor")
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Ano")
    garage_space = models.CharField(max_length=50, blank=True, verbose_name="Vaga de garagem")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "3. Veículo"
        verbose_name_plural = "3. Veículos"

    def __str__(self):
        return f"{self.license_plate} - {self.get_vehicle_type_display()}"

class Animal(models.Model):
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
    condo_unit = models.ForeignKey('CondominiumUnit', on_delete=models.CASCADE, related_name="animals", verbose_name="Unidade", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="Nome")
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES, default='dog', verbose_name="Espécie")
    breed = models.CharField(max_length=100, blank=True, verbose_name="Raça")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Idade")
    color = models.CharField(max_length=50, blank=True, verbose_name="Cor")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U', verbose_name="Sexo")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "5. Animal"
        verbose_name_plural = "5. Animais"

    def __str__(self):
        return self.name

