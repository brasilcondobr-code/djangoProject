from django.contrib import admin
from .models import (
    Shift, ServiceTransition, UsefulPhoneNumber, Order, 
    VisitorsRegister, Correspondence, Occurrence, Bag, Circular, Task
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

@admin.register(Circular)
class CircularAdmin(admin.ModelAdmin):
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
