from django.contrib import admin
from .models import Addresses, States, Condominium, TypesCondominium, StructionCondominium

# Register your models here.
@admin.register(TypesCondominium)
class TypesCondominiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

@admin.register(StructionCondominium)
class StructionCondominiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

@admin.register(States)
class StatesAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'capital', 'region')
    search_fields = ('name', 'abbreviation', 'capital', 'region')
    list_filter = ('name', 'abbreviation')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

@admin.register(Addresses)
class AddressesAdmin(admin.ModelAdmin):
    list_display = ( 'is_active', 'street', 'number', 'complement', 'city', 'state', 'country', 'zip_code')
    search_fields = ('street', 'city', 'state')
    list_filter = ('state',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

@admin.register(Condominium)
class CondominiumAdmin(admin.ModelAdmin):
    list_display = ('code','name', 'cnpj', 'is_active', 'state_registration', 'municipal_registration', 'type_condominium', 'address')
    search_fields = ('name', 'code', 'cnpj')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
