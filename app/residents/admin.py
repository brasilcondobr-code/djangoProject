import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Visitor, RealEstateAgency, Emergency, Vehicle, Animal, CondominiumUnit, Resident


class ExportCSVMixin:
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
    list_display = ('condo_unit', 'name', 'visit_date', 'is_active')
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
    list_display = ('condo_unit', 'name', 'phone', 'contact_person', 'is_active')
    search_fields = ('condo_unit__unit_number', 'name', 'contact_person')
    readonly_fields = ('created_at', 'updated_at', 'is_active')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')


@admin.register(Emergency)
class EmergencyAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('condo_unit', 'type', 'description', 'is_active')
    search_fields = ('condo_unit__unit_number', 'type', 'description')
    list_filter = ('condo_unit', 'type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')


@admin.register(Vehicle)
class VehicleAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('condo_unit', 'license_plate', 'vehicle_type', 'brand', 'model', 'color', 'is_active')
    search_fields = ('condo_unit__unit_number', 'license_plate')
    list_filter = ('condo_unit', 'vehicle_type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')


@admin.register(Animal)
class AnimalAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('condo_unit', 'name', 'species', 'is_active')
    search_fields = ('condo_unit__unit_number', 'name', 'species')
    list_filter = ('condo_unit', 'species', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condo_unit')


@admin.register(CondominiumUnit)
class CondominiumUnitAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('condominium', 'tower', 'unit_number', 'floor')
    search_fields = ('unit_number', 'condominium__name')
    list_filter = ('tower', 'floor')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['unit_number']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('condominium')


@admin.register(Resident)
class ResidentAdmin(ExportCSVMixin, admin.ModelAdmin):
    list_display = ('unit', 'name', 'type_of_resident', 'phone', 'email', 'is_active')
    search_fields = ('unit__unit_number', 'name', 'email')
    list_filter = ('type_of_resident', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('unit')

