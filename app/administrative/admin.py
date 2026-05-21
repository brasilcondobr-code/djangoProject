from django.contrib import admin
from .models import (
    Bank, Circular, Documents, Infraction, Meter, 
    Notification, Patrimony, BudgetForecast, ChartOfAccount, Task, VirtualAssembly
)
from .forms import BankForm

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    form = BankForm
    list_display = ('compe', 'bank_name', 'agency', 'account_number', 'account_digit', 'is_active')
    search_fields = ('bank_name', 'account_number', 'iban')
    list_filter = ('account_type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Principal', {
            'fields': (
                'compe', 'bank_name', 'account_type', 'initial_balance', 
                'initial_balance_date', 'account_name', 'iban', 'agency', 
                'account_number', 'account_digit', 'bank_address', 'is_active'
            )
        }),
        ('Beneficiário', {
            'fields': ('condominium',)
        }),
        ('Sacado Avalista', {
            'fields': (
                'full_name_drawn', 'cpf_drawn', 'rg_drawn', 
                'phone_drawn', 'email_drawn', 'addresses_drawn'
            )
        }),
        ('Gerente', {
            'fields': (
                'full_name_manager', 'phone1_manager', 'phone2_manager', 
                'phone3_manager', 'email_manager'
            )
        }),
    )

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/utils.js',
            'js/custom-administrative-bank.js',
        )

@admin.register(Circular)
class CircularAdmin(admin.ModelAdmin):
    pass

@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
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

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

@admin.register(VirtualAssembly)
class VirtualAssemblyAdmin(admin.ModelAdmin):
    pass
