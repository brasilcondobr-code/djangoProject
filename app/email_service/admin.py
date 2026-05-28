from django.contrib import admin, messages
from .forms import ConnectionStatusForm, TypesPriorityForm, TypesProviderForm, SMTPConfigurationForm
from .models import ConnectionStatus, TypesProvider, SMTPConfiguration, UsageProfiles, ShippingQueue, EmailHistory, TypesPriority
from core.services.smtp_validator_service import SMTPValidator

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

@admin.register(TypesPriority)
class TypesPriorityAdmin(admin.ModelAdmin):
    form = TypesPriorityForm
    list_display = ('priority', 'is_active')
    search_fields = ('priority',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    class Meta:
        model = TypesPriority
        verbose_name = "03. Tipo de Prioridade"
        verbose_name_plural = "03. Tipos de Prioridade"
        
    class Media:
        js = (
            'js/custom-emailservice-typespriority.js',
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
        'is_active',
        'connection_status',
        'last_connection_tested_at',
        'validation_attempts'
    )
    search_fields = (
        'description',
        'provider_code',
        'smtp_host'
    )
    list_filter = (
        'provider_type',
        'is_default',
        'is_active',
        'connection_status',
        'use_tls',
        'use_ssl'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'last_connection_tested_at',
        'last_successful_connection_at',
        'last_error_message',
        'last_validation_message',
        'last_response_time_ms',
        'validation_attempts'
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
            'fields': ('test_email_address', 'last_connection_tested_at', 'connection_status', 'last_error_message', 'last_test_duration', 'last_successful_connection_at', 'last_validation_message', 'last_response_time_ms', 'validation_attempts', 'connection_timeout'),
            'classes': ('collapse',),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['validate_smtp_connection']

    @admin.action(description="Validar conexão SMTP")
    def validate_smtp_connection(self, request, queryset):
        success_count = 0
        failed_count = 0

        for smtp in queryset:
            result = SMTPValidator.validate(
                smtp_config=smtp,
                user=request.user
            )

            if result["success"]:
                success_count += 1
            else:
                failed_count += 1

        if failed_count == 0:
            messages.success(
                request,
                f"Validação concluída: {success_count} sucesso(s), {failed_count} falha(s)"
            )
        else:
            messages.warning(
                request,
                f"Validação concluída: {success_count} sucesso(s), {failed_count} falha(s)"
            )

    class Media:
        js = (
            'js/custom-emailservice-smtpconfiguration.js',
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

