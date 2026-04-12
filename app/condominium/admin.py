import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Addresses, States, Condominium, TypesCondominium, StructionCondominium

# Register your models here.
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        
        # Gera o cabeçalho dinamicamente usando o 'verbose_name' configurado no Model
        writer.writerow([field.verbose_name.title() for field in meta.fields])
        
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    
    export_as_csv.short_description = "Exportar para CSV"


@admin.register(TypesCondominium)
class TypesCondominiumAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    

@admin.register(StructionCondominium)
class StructionCondominiumAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    

@admin.register(States)
class StatesAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'capital', 'region')
    search_fields = ('name', 'abbreviation', 'capital', 'region')
    list_filter = ('name', 'abbreviation')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    

@admin.register(Addresses)
class AddressesAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ( 'street', 'number', 'neighborhood', 'city', 'state', 'is_active')
    search_fields = ('street', 'city', 'state')
    list_filter = ('state','city', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    

@admin.register(Condominium)
class CondominiumAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ('code','name', 'cnpj', 'state_registration', 'municipal_registration', 'type_condominium', 'address', 'is_active')
    search_fields = ('name', 'code', 'cnpj')
    list_filter = ('code', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
