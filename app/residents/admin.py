import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Documents, Visitor, RealEstateAgency, Emergency, Vehicle, Animal, CondominiumUnit, Resident
from .forms import CondominiumUnitFormAdmin, ResidentFormAdmin, VehicleFormAdmin

class ExportCSVMixin:
    def init(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)
        
    def export_as_csv(self, request, queryset):
        model_name = self.model._meta.model_name
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={model_name}.csv'
        writer = csv.writer(response)

        writer.writerow([field.name for field in self.model._meta.fields])
        for obj in queryset:
            writer.writerow([getattr(obj, field.name) for field in self.model._meta.fields])

        return response

    export_as_csv.short_description = "Exportar para CSV"
    actions = ['export_as_csv']


@admin.register(Visitor)
class VisitorAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('name', 'visit_date', 'condo_unit', 'is_active')
    search_fields = ('condo_unit__unit_number', 'name')
    list_filter = ('condo_unit', 'visit_date', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-visit_date']
    date_hierarchy = 'visit_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')


@admin.register(RealEstateAgency)
class RealEstateAgencyAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('name', 'phone', 'contact_person', 'condo_unit', 'is_active')
    search_fields = ('condo_unit__unit_number', 'name', 'contact_person')
    readonly_fields = ('created_at', 'updated_at', 'is_active')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')


@admin.register(Emergency)
class EmergencyAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('type', 'description', 'condo_unit', 'is_active')
    search_fields = ('condo_unit__unit_number', 'type', 'description')
    list_filter = ('condo_unit', 'type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')


@admin.register(Vehicle)
class VehicleAdmin(ExportCSVMixin, admin.ModelAdmin):
    form = VehicleFormAdmin
    list_display = ('license_plate', 'vehicle_type', 'brand', 'model', 'color', 'condo_unit', 'is_active')
    search_fields = ('condo_unit__unit_number', 'license_plate')
    list_filter = ('condo_unit', 'vehicle_type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')
    
    class Media:
        js = (
            'js/jquery-4.0.0.min.js',
            'js/custom-admin-vehicle.js',
        )


@admin.register(Animal)
class AnimalAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('name', 'species', 'condo_unit', 'is_active')
    search_fields = ('condo_unit__unit_number', 'name', 'species')
    list_filter = ('condo_unit', 'species', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')


@admin.register(CondominiumUnit)
class CondominiumUnitAdmin(ExportCSVMixin, admin.ModelAdmin):
    form = CondominiumUnitFormAdmin
    list_display = ('identification', 'tower', 'unit_number', 'floor', 'condominium')
    search_fields = ('unit_number', 'condominium__name')
    list_filter = ('tower', 'floor')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['unit_number']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condominium')
    
    class Media:
        js = (
            'js/jquery-4.0.0.min.js',
            'js/custom-admin-condominium-unit.js',
        )


@admin.register(Resident)
class ResidentAdmin(ExportCSVMixin, admin.ModelAdmin):
    form = ResidentFormAdmin
    list_display = ('name', 'type_of_resident', 'phone', 'email', 'unit', 'is_active')
    search_fields = ('unit__unit_number', 'name', 'email')
    list_filter = ('type_of_resident', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('unit')
    
    class Media:
        js = (
            'js/jquery-4.0.0.min.js',
            'js/custom-admin-resident.js',
        )


@admin.register(Documents)
class DocumentsAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('title','document_type', 'file', 'condo_unit', 'is_active')
    search_fields = ('condo_unit__unit_number', 'document_type', 'title')
    list_filter = ('document_type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')
