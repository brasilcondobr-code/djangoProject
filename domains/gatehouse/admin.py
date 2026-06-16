from django.contrib import admin
from domains.gatehouse.models import (
    ElectronicTimeClock, Shift, ServiceTransition, UsefulPhoneNumber, Order, 
    VisitorsRegister, Correspondence, Occurrence, Bag,
)

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    pass

@admin.register(ServiceTransition)
class ServiceTransitionAdmin(admin.ModelAdmin):
    pass

@admin.register(UsefulPhoneNumber)
class UsefulPhoneNumberAdmin(admin.ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(VisitorsRegister)
class VisitorsRegisterAdmin(admin.ModelAdmin):
    pass

@admin.register(Correspondence)
class CorrespondenceAdmin(admin.ModelAdmin):
    pass

@admin.register(Occurrence)
class OccurrenceAdmin(admin.ModelAdmin):
    pass

@admin.register(Bag)
class BagAdmin(admin.ModelAdmin):
    pass

@admin.register(ElectronicTimeClock)
class ElectronicTimeClockAdmin(admin.ModelAdmin):
    pass

