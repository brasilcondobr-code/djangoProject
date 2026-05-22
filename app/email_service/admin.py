from django.contrib import admin

from .forms import ConnectionStatusForm, TypesProviderForm
from .models import ConnectionStatus, TypesProvider, SMTP_Settings, UsageProfiles, ShippingQueue, EmailHistory

@admin.register(TypesProvider)
class TypesProviderAdmin(admin.ModelAdmin):
    form = TypesProviderForm
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    class Meta:
        model = TypesProvider
        verbose_name = "01. Tipo de Provedor"
        verbose_name_plural = "01. Tipos de Provedores"
        
    class Media:
        js = (
            'js/custom-emailservice-typesprovider.js',
            )
    
@admin.register(ConnectionStatus)
class ConnectionStatusAdmin(admin.ModelAdmin):
    form = ConnectionStatusForm
    list_display = ('provider', 'status', 'last_checked')
    search_fields = ('provider__name',)
    list_filter = ('status',)
    readonly_fields = ('last_checked',)
    list_per_page = 25
    
    class Meta:
        model = ConnectionStatus
        verbose_name = "02. Status de Conexão"
        verbose_name_plural = "02. Status de Conexão"
        
    class Media:
        js = (
            'js/custom-emailservice-connectionstatus.js',
            )
    
@admin.register(SMTP_Settings)
class SMTP_SettingsAdmin(admin.ModelAdmin):
    pass

@admin.register(UsageProfiles)
class UsageProfilesAdmin(admin.ModelAdmin):
    pass

@admin.register(ShippingQueue)
class ShippingQueueAdmin(admin.ModelAdmin):
    pass

@admin.register(EmailHistory)
class EmailHistoryAdmin(admin.ModelAdmin):
    pass
