import csv

from django.contrib import admin
from django.http import HttpResponse

from .forms import BankForm
from domains.administrative.models import Bank
from domains.administrative.models.circular import Circular
from domains.administrative.models.documents import Documents
from domains.administrative.models.infraction import Infraction
from domains.administrative.models.meter import Meter
from domains.administrative.models.notification import Notification
from domains.administrative.models.patrimony import Patrimony
from domains.administrative.models.budget_forecast import BudgetForecast
from domains.administrative.models.chart_of_account import ChartOfAccount
from domains.administrative.models.task import Task
from domains.administrative.models.virtual_assembly import VirtualAssembly

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

# Register your models here.
@admin.register(Bank)
class BankAdmin(ExportCsvMixin, admin.ModelAdmin):
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
