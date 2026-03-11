import csv
from django.http import HttpResponse
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
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(['id','Descrição', 'Ativo', 'Criado em', 'Atualizado em'])
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    
    export_as_csv.short_description = "Exportar para CSV"
    actions = ["export_as_csv"]
    

@admin.register(StructionCondominium)
class StructionCondominiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(['id','Descrição', 'Ativo', 'Criado em', 'Atualizado em'])
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    
    export_as_csv.short_description = "Exportar para CSV"
    actions = ["export_as_csv"]
    

@admin.register(States)
class StatesAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'capital', 'region')
    search_fields = ('name', 'abbreviation', 'capital', 'region')
    list_filter = ('name', 'abbreviation')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(['id','Nome', 'Abreviação', 'Capital', 'Região', 'Criado em', 'Atualizado em'])
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    
    export_as_csv.short_description = "Exportar para CSV"
    actions = ["export_as_csv"]
    

@admin.register(Addresses)
class AddressesAdmin(admin.ModelAdmin):
    list_display = ( 'is_active', 'street', 'number', 'complement', 'city', 'state', 'country', 'zip_code')
    search_fields = ('street', 'city', 'state')
    list_filter = ('state',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(['id','Ativo', 'Logradouro', 'Número', 'Complemento', 'Cidade', 'Estado', 'País', 'CEP', 'Criado em', 'Atualizado em'])
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    
    export_as_csv.short_description = "Exportar para CSV"
    actions = ["export_as_csv"]
    

@admin.register(Condominium)
class CondominiumAdmin(admin.ModelAdmin):
    list_display = ('code','name', 'cnpj', 'is_active', 'state_registration', 'municipal_registration', 'type_condominium', 'address')
    search_fields = ('name', 'code', 'cnpj')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(['id','Código', 'Nome', 'CNPJ', 'Ativo', 'Inscrição Estadual', 'Inscrição Municipal', 'Tipo de Condomínio', 'Estrutura do Condomínio', 'Endereço', 'Criado em', 'Atualizado em'])
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    
    export_as_csv.short_description = "Exportar para CSV"
    actions = ["export_as_csv"]

