from django.contrib import admin
from .models import (
    Bank, Circular, Contract, Infraction, Meter, 
    Notification, Patrimony, BudgetForecast, ChartOfAccount, Project, Task
)

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    pass

@admin.register(Circular)
class CircularAdmin(admin.ModelAdmin):
    pass

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    pass

@admin.register(Infraction)
class InfractionAdmin(admin.ModelAdmin):
    pass

@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    pass

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass

@admin.register(Patrimony)
class PatrimonyAdmin(admin.ModelAdmin):
    pass

@admin.register(BudgetForecast)
class BudgetForecastAdmin(admin.ModelAdmin):
    pass

@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    pass

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
