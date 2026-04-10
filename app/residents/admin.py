from django.contrib import admin
from .models import Visitor, RealEstateAgency, Emergency, Vehicle, Animal, CondominiumUnit, Resident

# Register your models here.
@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'visit_date')
    search_fields = ('name', 'host')
    list_filter = ('visit_date',)

@admin.register(RealEstateAgency)
class RealEstateAgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'active')
    search_fields = ('name',)

@admin.register(Emergency)
class EmergencyAdmin(admin.ModelAdmin):
    list_display = ('type', 'occurred_at', 'condo_unit')
    search_fields = ('type', 'description')
    list_filter = ('type',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'vehicle_type')
    search_fields = ('license_plate', 'owner__name')
    list_filter = ('vehicle_type',)

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'owner')
    search_fields = ('name', 'species', 'owner__name')
    list_filter = ('species',)

@admin.register(CondominiumUnit)
class CondominiumUnitAdmin(admin.ModelAdmin):
    list_display = ('condominium', 'tower', 'unit_number', 'floor')
    search_fields = ('unit_number', 'condominium__name')
    list_filter = ('tower', 'floor')

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'phone', 'email')
    search_fields = ('name', 'unit', 'email')
    list_filter = ('name', 'unit', 'email')
    readonly_fields = ('created_at', 'updated_at')
