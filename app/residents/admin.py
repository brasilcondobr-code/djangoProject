from django.contrib import admin
from .models import Visitor, RealEstateAgency, Emergency, Vehicle, Animal, CondominiumUnit, Resident

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


# Register your models here.
@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('condo_unit', 'name', 'visit_date')
    search_fields = ('condo_unit__unit_number', 'name')
    list_filter = ('condo_unit', 'visit_date')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_as_csv']
    list_per_page = 25

@admin.register(RealEstateAgency)
class RealEstateAgencyAdmin(admin.ModelAdmin):
    list_display = ('condo_unit', 'name', 'phone', 'contact_person', 'active')
    search_fields = ('condo_unit__unit_number', 'name', 'contact_person')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_as_csv']
    list_per_page = 25

@admin.register(Emergency)
class EmergencyAdmin(admin.ModelAdmin):
    list_display = ('condo_unit', 'type', 'description')
    search_fields = ('condo_unit__unit_number', 'type', 'description')
    list_filter = ('condo_unit', 'type')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_as_csv']
    list_per_page = 25

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('condo_unit', 'license_plate', 'vehicle_type', 'brand', 'model', 'color')
    search_fields = ('condo_unit__unit_number', 'license_plate')
    list_filter = ('condo_unit', 'vehicle_type',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_as_csv']
    list_per_page = 25

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('condo_unit', 'name', 'species')
    search_fields = ('condo_unit__unit_number', 'name', 'species')
    list_filter = ('condo_unit', 'species')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_as_csv']
    list_per_page = 25


@admin.register(CondominiumUnit)
class CondominiumUnitAdmin(admin.ModelAdmin):
    list_display = ('condominium', 'tower', 'unit_number', 'floor')
    search_fields = ('unit_number', 'condominium__name')
    list_filter = ('tower', 'floor')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_as_csv']
    list_per_page = 25

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'phone', 'email')
    search_fields = ('name', 'unit', 'email')
    list_filter = ('name', 'unit', 'email')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_as_csv']
    list_per_page = 25
