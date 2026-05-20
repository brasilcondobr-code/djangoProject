import decimal
from email.policy import default

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
    area_total = models.DecimalField(default=decimal.Decimal('60.00'), max_digits=10, decimal_places=2, verbose_name="Área total")

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
        ordering = ["tower", "unit_number", "floor", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["tower", "unit_number"], name="unique_unit_per_tower")
        ]
        verbose_name = "01. Unidade"
        verbose_name_plural = "01. Unidades"
        unique_together = (("tower", "unit_number"),)
    
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
    

class Resident(models.Model):
    RECEITA_STATUS_CHOICES = (
        ('Regular', 'Regular'),
        ('Suspenso', 'Suspenso'),
        ('Pendente de Regularização', 'Pendente de Regularização'),
        ('Cancelado', 'Cancelado'),
        ('Titular Falecido', 'Titular Falecido'),
        ('Nulo', 'Nulo'),
    )
    YES_NO_CHOICES = (
        ('Sim', 'Sim'),
        ('Não', 'Não'),
    )

    ResidentTypeChoices = [
        ('owner', 'Proprietário(a)'),
        ('tenant', 'Morador(a)'),
        ('occupant', 'Ocupante'),
    ]
    
    unit = models.ForeignKey(CondominiumUnit, on_delete=models.CASCADE, related_name="residents", verbose_name="Unidade")
    type_of_resident = models.CharField(max_length=20, choices=ResidentTypeChoices, default='tenant', null=True, blank=True, verbose_name="Tipo de morador")
    name = models.CharField(max_length=250, verbose_name="Nome")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    cpf = models.CharField(max_length=14, verbose_name="CPF")
    rg = models.CharField(max_length=20, verbose_name="RG")
    sex = models.CharField(max_length=1, choices=SexChoices.choices, verbose_name="Sexo")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Data de nascimento")
    profission = models.CharField(max_length=100, blank=True, verbose_name="Profissão")
    is_primary = models.BooleanField(default=False, verbose_name="Principal")
    is_resident = models.BooleanField(default=True, verbose_name="É residente")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    photo = models.ImageField(upload_to='residents/photos/', null=True, blank=True, verbose_name="Foto")
    
    situation = models.CharField(
        max_length=100,
        choices=RECEITA_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Situação Receita Federal"
    )
    regular = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        null=True,
        blank=True,
        verbose_name="CPF Regular"
    )
    death = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Óbito"
    )
    api_status = models.CharField(
        max_length=100,
        default='nulo',
        null=True,
        blank=True,
        editable=False,
        verbose_name="Status da API"
    )
    retorno_api = models.TextField(
        default='nulo',
        null=True,
        blank=True,
        editable=False,
        verbose_name='Retorno da API'
    )
    date_time_appointment = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
        editable=False,
        verbose_name='Data/hora da consulta'
    )
    certificate_presentation_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data de apresentação da certidão"
    )
    certificate_validity = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Validade da certidão"
    )
    observations_certificate = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Observações da certidão"
    )
    certificate_file = models.FileField(
        upload_to='residents/certidoes/', 
        null=True, 
        blank=True, 
        verbose_name="Arquivo da certidão"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criдо em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ["unit", "name", "created_at"]
        verbose_name = "0  02. Morador"
        verbose_name_plural = "02. Moradores"
        unique_together = (("unit", "name"), ("unit", "cpf"), ("unit", "rg"))

    def __str__(self):
        return f"{self.name} | {self.unit}".strip()


class Visitor(models.Model):
    condo_unit = models.ForeignKey('residents.CondominiumUnit', on_delete=models.CASCADE, null=True, blank=True, related_name="visitors", verbose_name="Condomínio/Unidade")
    name = models.CharField(max_length=250, verbose_name="Nome")
    cpf = models.CharField(max_length=14, verbose_name="CPF")
    rg = models.CharField(max_length=20, verbose_name="RG")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    purpose = models.CharField(max_length=255, blank=True, verbose_name="Propósito da visita")
    photo = models.ImageField(upload_to='residents/visitors/', null=True, blank=True, verbose_name="Foto")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    situation = models.CharField(
        max_length=100,
        choices=Resident.RECEITA_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Situação Receita Federal"
    )
    regular = models.CharField(
        max_length=3,
        choices=Resident.YES_NO_CHOICES,
        null=True,
        blank=True,
        verbose_name="CPF Regular"
    )
    death = models.CharField(
        max_length=3,
        choices=Resident.YES_NO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Óbito"
    )
    api_status = models.CharField(
        max_length=100,
        default='nulo',
        null=True,
        blank=True,
        editable=False,
        verbose_name="Status da API"
    )
    retorno_api = models.TextField(
        default='nulo',
        null=True,
        blank=True,
        editable=False,
        verbose_name='Retorno da API'
    )
    date_time_appointment = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
        editable=False,
        verbose_name='Data/hora da consulta'
    )
    certificate_presentation_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data de apresentação da certidão"
    )
    certificate_validity = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Validade da certidão"
    )
    observations_certificate = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Observações da certidão"
    )
    certificate_file = models.FileField(
        upload_to='residents/certidoes/', 
        null=True, 
        blank=True, 
        verbose_name="Arquivo da certidão"
    )
    types_visitor_restriction = models.ForeignKey(
        'parameters.TypesVisitorRestrictions', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Tipos de Restrição"
    )
    restrictionVisitor_presentation_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data de apresentação"
    )
    restrictionVisitor_validity_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data de validade"
    )
    restrictionVisitor_observations = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Observações"
    )
    restrictionVisitor_file = models.FileField(
        upload_to='residents/restrictions/', 
        null=True, 
        blank=True, 
        verbose_name="Arquivo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["condo_unit", "name", "created_at"]
        verbose_name = "06. Visitante"
        verbose_name_plural = "06. Visitantes"
        unique_together = (("condo_unit", "name"), ("condo_unit", "cpf"), ("condo_unit", "rg"))

    def __str__(self):
        return f"{self.name} | {self.condo_unit}".strip()
            

class RealEstateAgency(models.Model):
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

    class Meta:
        ordering = ["condo_unit", "name", "created_at"]
        verbose_name = "07. Imobiliária"
        verbose_name_plural = "07. Imobiliárias"
        unique_together = (("condo_unit", "name"), ("condo_unit", "email"), ("condo_unit", "phone"))

    def __str__(self):
        return self.name

class Emergency(models.Model):
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
    condo_unit = models.ForeignKey('residents.CondominiumUnit', on_delete=models.CASCADE, null=True, blank=True, related_name='emergencies', verbose_name="Condomínio/Unidade")
    type = models.CharField(max_length=20, choices=EMERGENCY_CHOICES, default='other', verbose_name="Tipo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    occurred_at = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["condo_unit", "type", "occurred_at", "created_at"]
        verbose_name = "04. Emergência"
        verbose_name_plural = "04. Emergências"
        unique_together = (("condo_unit", "type", "occurred_at"), ("condo_unit", "description", "occurred_at"))

    def __str__(self):
        return f"{self.type} | {self.condo_unit}".strip()

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
    condo_unit = models.ForeignKey('residents.CondominiumUnit', on_delete=models.CASCADE, null=True, blank=True, related_name="vehicles", verbose_name="Condomínio/Unidade")
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

    class Meta:
        ordering = ["condo_unit", "vehicle_type", "license_plate", "created_at"]
        verbose_name = "03. Veículo"
        verbose_name_plural = "03. Veículos"
        unique_together = (("condo_unit", "license_plate"), ("condo_unit", "vehicle_type", "model", "year"))

    def __str__(self):
        return self.license_plate

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
    condo_unit = models.ForeignKey('CondominiumUnit', on_delete=models.CASCADE, related_name="animals", verbose_name="Condomínio/Unidade", null=True, blank=True)
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

    class Meta:
        ordering = ["condo_unit", "name", "species", "created_at"]
        verbose_name = "05. Animal"
        verbose_name_plural = "05. Animais"
        unique_together = (("condo_unit", "name"), ("condo_unit", "species", "breed"))

    def __str__(self):
        return self.name


class Documents(models.Model):
    DOCTYPES_CHOICES = [
        ('personal', 'Documentos Pessoais'),
        ('cadastral', 'Cadastrais'),
        ('contracts', 'Contratos'),
        ('receipts', 'Comprovantes'),
        ('TAX', 'Documentos Fiscais'),
        ('vehicle_data', 'Dados de veículos'),
        ('animal_data', 'Dados de animais'),
        ('other', 'Outros'),
    ]
    condo_unit = models.ForeignKey('residents.CondominiumUnit', on_delete=models.CASCADE, related_name="documents", verbose_name="Condomínio/Unidade", null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="Título")
    document_type = models.CharField(max_length=20, choices=DOCTYPES_CHOICES, default='personal', verbose_name="Tipo de documento")
    file = models.FileField(upload_to='documents/', null=True, blank=True, verbose_name="Arquivo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["condo_unit", "title", "created_at"]
        verbose_name = "08. Documento"
        verbose_name_plural = "08. Documentos"
        unique_together = (("condo_unit", "title"), ("condo_unit", "document_type", "created_at"))

    def __str__(self):
        return self.title