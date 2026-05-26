from django.contrib import admin

from .forms import ConnectionStatusForm, TypesProviderForm, SMTPConfigurationForm
from .models import ConnectionStatus, TypesProvider, SMTPConfiguration, UsageProfiles, ShippingQueue, EmailHistory

@admin.register(TypesProvider)
class TypesProviderAdmin(admin.ModelAdmin):
    form = TypesProviderForm
    list_display = ('provider', 'is_active')
    search_fields = ('provider',)
    list_filter = ('is_active',)
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
    list_display = ('status', 'description', 'is_active')
    search_fields = ('status',)
    list_filter = ('status', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    class Meta:
        model = ConnectionStatus
        verbose_name = "02. Status de Conexão"
        verbose_name_plural = "02. Status de Conexão"
        
    class Media:
        js = (
            'js/custom-emailservice-connectionstatus.js',
            )

@admin.register(SMTPConfiguration)
class SMTPConfigurationAdmin(admin.ModelAdmin):
    form = SMTPConfigurationForm
    list_display = (
        'description',
        'provider_type',
        'smtp_host',
        'smtp_port',
        'is_default',
        'is_active'
    )
    search_fields = (
        'description',
        'provider_code',
        'smtp_host'
    )
    list_filter = (
        'provider_type',
        'is_default',
        'is_active'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'last_connection_tested_at'
    )
    
    fieldsets = (
        ('Principal', {
            'fields': (
                'description', 'provider_code', 'provider_type', 
                'smtp_host', 'smtp_port', 'username', 'password', 
                'use_tls', 'use_ssl', 'smtp_authentication', 
                'api_supported', 'is_default', 'is_active'
            )
        }),
        ('Configuração API', {
            'fields': ('api_url', 'api_key', 'api_secret', 'api_version'),
            'classes': ('collapse',),
        }),
        ('Limites', {
            'fields': ('emails_per_hour', 'emails_per_day', 'max_recipients_per_email'),
            'classes': ('collapse',),
        }),
        ('Testes e Monitoramento', {
            'fields': ('test_email_address', 'last_connection_tested_at', 'connection_status'),
            'classes': ('collapse',),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    class Media:
        js = (
            'js/custom-emailservice-emailprovider.js',
            )

@admin.register(UsageProfiles)
class UsageProfilesAdmin(admin.ModelAdmin):
    list_display = (
        'purpose',
        'is_active',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'is_active',
    )
    search_fields = (
        'purpose',
    )
    ordering = (
        'purpose',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (
            'Principal',
            {
                'fields': (
                    'purpose',
                    'is_active'
                )
            }
        ),
        (
            'Auditoria',
            {
                'fields': (
                    'created_at',
                    'updated_at'
                )
            }
        ),
    )

    @admin.action(description='Ativar registros selecionados')
    def activate_profiles(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Desativar registros selecionados')
    def deactivate_profiles(self, request, queryset):
        queryset.update(is_active=False)

    actions = ['activate_profiles', 'deactivate_profiles']
    
    class Meta:
        model = UsageProfiles
        verbose_name = "03. Perfil de Utilização"
        verbose_name_plural = "03. Perfis de Utilização"
        
    class Media:
        js = (
            'js/custom-emailservice-usageprofiles.js',
            )


@admin.register(ShippingQueue)
class ShippingQueueAdmin(admin.ModelAdmin):
    pass

@admin.register(EmailHistory)
class EmailHistoryAdmin(admin.ModelAdmin):
    pass

