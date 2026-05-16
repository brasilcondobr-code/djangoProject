import csv
from django.http import HttpResponse
from django.contrib import admin

from .forms import CondominiumFormAdmin, CollaboratorsFormAdmin
from .models import Condominium, Collaborators, DocumentCondominium, Types_collaborators

# Register your models here.
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
        
        # Gera o cabeçalho dinamicamente usando o 'verbose_name' configurado no Model
        writer.writerow([field.verbose_name.title() for field in meta.fields])
        
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    
    export_as_csv.short_description = "Exportar para CSV"


@admin.register(Condominium)
class CondominiumAdmin(ExportCsvMixin, admin.ModelAdmin):
    form = CondominiumFormAdmin
    list_display = ('code','name', 'cnpj', 'state_registration', 'municipal_registration', 'type_condominium', 'address', 'is_active')
    search_fields = ('name', 'code', 'cnpj')
    list_filter = ('code', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    
    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/custom-admin-condominium.js',
        )
    
    class Meta:
        model = Condominium
    
@admin.register(Types_collaborators)
class TypesCollaboratorsAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]

@admin.register(Collaborators)
class CollaboratorsAdmin(ExportCsvMixin, admin.ModelAdmin):
    form = CollaboratorsFormAdmin
    list_display = ('name', 'email', 'phone_number', 'type_collaborator', 'condominium', 'photo', 'is_active')
    search_fields = ('condominium__name', 'name', 'email')
    list_filter = ('condominium', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'api_status', 'retorno_api', 'date_time_appointment')
    list_per_page = 25
    actions = ["export_as_csv"]
    
    fieldsets = (
        (None, {
            'fields': (
                'condominium',
                'name',
                'cpf',
                'rg',
                'email',
                'phone_number',
                'type_collaborator',
                'is_active',
                'photo',
                'observations',
            )
        }),
        ('Receita Federal', {
            'fields': ('situation', 'regular', 'death', 'api_status', 'retorno_api', 'date_time_appointment'),
        }),
    )
    
    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/custom-admin-collaborators.js',
        )
        
    class Meta:
        model = Collaborators

@admin.register(DocumentCondominium)
class DocumentCondominiumAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ('condominium', 'name', 'file', 'is_active')
    search_fields = ('condominium__name', 'name')
    list_filter = ('condominium', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    actions = ["export_as_csv"]
    
    class Meta:
        model = DocumentCondominium
        
    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/custom-condominium-documentcondominium.js',
        )
        