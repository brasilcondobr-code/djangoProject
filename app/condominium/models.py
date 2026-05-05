from django.db import models

# Create your models here.
class TypesCondominium(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name="Tipo de Condomínio")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "1. Tipo de Condomínio"
        verbose_name_plural = "1. Tipos de Condomínios"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
    
    def __str__(self):
        return self.name

class StructionCondominium(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name="Estrutura do Condomínio")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "2. Estrutura do Condomínio"
        verbose_name_plural = "2. Estruturas dos Condomínios"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
    
    def __str__(self):
        return self.name

class States(models.Model):
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

    class Meta:
        verbose_name = "3. Estado"
        verbose_name_plural = "3. Estados"
        ordering = ["abbreviation", "name", "region"]
        unique_together = ['name', 'abbreviation']

    def __str__(self):
        return self.name


class Addresses(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    street = models.CharField(max_length=255, null=False, blank=False,verbose_name="Logradouro")
    number = models.IntegerField(null=False, blank=False,verbose_name="Número")
    complement = models.CharField(max_length=255, null=False, blank=True, verbose_name="Complemento")
    neighborhood = models.CharField(max_length=255, null=True, blank=True, verbose_name="Bairro")
    city = models.CharField(max_length=100, null=False, blank=False, verbose_name="Município")
    state = models.ForeignKey(States, related_name="address", null=False, blank=False, verbose_name="UF", on_delete=models.CASCADE)
    country = models.CharField(max_length=100, null=False, blank=False, default="Brasil", verbose_name="País")
    zip_code = models.CharField(max_length=20, null=False, blank=False, verbose_name="CEP")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "4. Endereço"
        verbose_name_plural = "4. Endereços"
        ordering = ["country", 'state', 'city', 'street', 'number', 'complement', "is_active", "created_at"]
        unique_together = ['street', 'number', 'neighborhood', 'city', 'state', 'zip_code']
        

    def __str__(self):
        address_line = f"{self.street}, {self.number}"
        if self.complement:
            address_line += f" - {self.complement}"
        return f"{address_line} | {self.neighborhood} | {self.city}/{self.state.abbreviation} | {self.zip_code}"

class Condominium(models.Model):
    code = models.CharField(max_length=100, verbose_name="Código", unique=True)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome")
    cnpj = models.CharField(max_length=20, null=False, blank=False, verbose_name="CNPJ", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
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
    
    class Meta:
        verbose_name = "5. Condomínio"
        verbose_name_plural = "5. Condomínios"
        ordering = ["name", "code", "cnpj", "is_active", "created_at"]
        ##unique_together = [['cnpj'], ['code']]

    def __str__(self):
        return self.name
    

class Types_collaborators(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name="Tipo de Colaborador")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "6. Tipo de Colaborador"
        verbose_name_plural = "6. Tipos de Colaboradores"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
    
    def __str__(self):
        return self.name


class Collaborators(models.Model):
    condominium = models.ForeignKey(Condominium, related_name="collaborators", null=False, blank=False, verbose_name="Condomínio", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome")
    cpf = models.CharField(max_length=20, null=False, blank=False, verbose_name="CPF", unique=True)
    rg = models.CharField(max_length=20, null=False, blank=False, verbose_name="RG")
    email = models.EmailField(max_length=255, null=False, blank=False, verbose_name="Email", unique=True)
    phone_number = models.CharField(max_length=20, null=False, blank=False, verbose_name="Telefone")
    type_collaborator = models.ForeignKey(Types_collaborators, related_name="Types_collaborators", null=True, blank=False, verbose_name="Tipo de Colaborador", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    observations = models.TextField(null=True, blank=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "7. Colaborador"
        verbose_name_plural = "7. Colaboradores"
        ordering = ["name", "email", "phone_number", "created_at"]
        unique_together = [['name', 'cpf'], ['condominium', 'cpf']]

    def __str__(self):
        return self.name