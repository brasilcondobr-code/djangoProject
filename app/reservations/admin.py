from django.contrib import admin
from .models import Reforms, Rentals, MaintenanceReservations, MoveReservations

@admin.register(Rentals)
class RentalsAdmin(admin.ModelAdmin):
    pass

@admin.register(MaintenanceReservations)
class MaintenanceReservationsAdmin(admin.ModelAdmin):
    pass

@admin.register(MoveReservations)
class MoveReservationsAdmin(admin.ModelAdmin):
    pass

@admin.register(Reforms)
class ReformsAdmin(admin.ModelAdmin):
    pass
