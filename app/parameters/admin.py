import csv
from django.http import HttpResponse
from django.contrib import admin

from .models import Addresses, States, TypesCondominium, StructionCondominium
from .forms import AddressesForm, StatesForm

class ExportCsvMixin:
    def init(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
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
    
    class Meta:
        verbose_name = "1. Tipo de Condomínio"
        verbose_name_plural = "1. Tipos de Condomínios"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
        db_table = 'condominium_typescondominium'


@admin.register(StructionCondominium)
class StructionCondominiumAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    
    class Meta:
        verbose_name = "2. Estrutura do Condomínio"
        verbose_name_plural = "2. Estruturas dos Condomínios"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
        db_table = 'condominium_structioncondominium'


@admin.register(States)
class StatesAdmin(ExportCsvMixin, admin.ModelAdmin):
    form = StatesForm
    list_display = ('name', 'abbreviation', 'capital', 'region')
    search_fields = ('name', 'abbreviation', 'capital', 'region')
    list_filter = ('name', 'abbreviation')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    
    class Meta:
        verbose_name = "3. Estado"
        verbose_name_plural = "3. Estados"
        ordering = ["abbreviation", "name", "region"]
        unique_together = ['name', 'abbreviation']
        db_table = 'condominium_states'
        
    class Media:
        js = (
            'js/custom-admin-states.js',
            )


@admin.register(Addresses)
class AddressesAdmin(ExportCsvMixin, admin.ModelAdmin):
    form = AddressesForm
    list_display = ('street', 'number', 'neighborhood', 'city', 'state', 'is_active')
    search_fields = ('street', 'city', 'state')
    list_filter = ('state', 'city', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    
    class Meta:
        verbose_name = "4. Endereço"
        verbose_name_plural = "4. Endereços"
        ordering = ["street", "number", "city", "state", "is_active", "created_at"]
        db_table = 'condominium_addresses'
        unique_together = ['street', 'number', 'neighborhood', 'city', 'state', 'zip_code']
        
    class Media:
        js = (
            'js/custom-admin-address.js',
            )
        
