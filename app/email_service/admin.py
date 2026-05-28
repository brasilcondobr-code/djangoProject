from django.contrib import admin, messages
from .forms import ConnectionStatusForm, TypesProviderForm, SMTPConfigurationForm
from .models import ConnectionStatus, TypesProvider, SMTPConfiguration, UsageProfiles, ShippingQueue, EmailHistory, TypesPriority
from core.services.smtp_validator_service import SMTPValidator
from email_service.services.queue_processor_service import QueueProcessorService
from email_service.services.retry_service import RetryService

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
    list_display = ('priority', 'is_active')
    search_fields = ('priority',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    class Meta:
        model = TypesPriority
        verbose_name = "03. Tipo de Prioridade"
        verbose_name_plural = "03. Tipos de Prioridade"
    
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
            'fields': ('test_email_address', 'last_connection_tested_at', 'connection_status', 'last_error_message', 'last_test_duration'),
            'classes': ('collapse',),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
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
                    'updated_at',
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
    list_display = (
        'subject',
        'to_email',
        'status',
        'priority',
        'retry_count',
        'is_active'
    )
    list_filter = (
        'status',
        'priority',
        'usage_profile',
        'smtp_configuration',
        'is_active',
    )
    search_fields = (
        'subject',
        'to_email',
        'provider_message_id',
        'uuid',
    )
    readonly_fields = (
        'uuid',
        'retry_count',
        'provider_response',
        'response_time_ms',
        'provider_message_id',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        ('Principal', {
            'fields': (
                'condominium', 'module_origin', 'reference_id', 'uuid',
                'subject', 'to_email', 'cc', 'bcc', 'reply_to',
                'message', 'html_message', 'attachments'
            )
        }),
        ('Configuração', {
            'fields': ('smtp_configuration', 'usage_profile', 'priority', 'scheduled_at'),
            'classes': ('collapse',),
        }),
        ('Processamento', {
            'fields': ('is_active', 'status', 'processing_started_at', 'sent_at', 'retry_count', 'max_retry_attempts', 'next_retry_at'),
            'classes': ('collapse',),
        }),
        ('Auditoria', {
            'fields': ('last_error_message', 'provider_response', 'logs', 'response_time_ms', 'provider_message_id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ['reprocess_queue', 'cancel_sending', 'mark_as_sent', 'export_logs']

    @admin.action(description="Reprocessar fila")
    def reprocess_queue(self, request, queryset):
        count = 0
        for item in queryset:
            item.is_active = True
            item.retry_count = 0
            item.next_retry_at = None
            item.save()
            count += 1
        self.message_user(request, f"{count} itens foram resetados para reprocessamento.")

    @admin.action(description="Cancelar envio")
    def cancel_sending(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} envios foram cancelados.")

    @admin.action(description="Marcar como enviado")
    def mark_as_sent(self, request, queryset):
        for item in queryset:
            item.sent_at = timezone.now()
            item.is_active = False
            item.save()
        self.message_user(request, f"{queryset.count()} itens marcados como enviados.")

    @admin.action(description="Realizar envio")
    def perform_send(self, request, queryset):
        success_count = 0
        failure_count = 0
        for item in queryset:
            result = QueueProcessorService.process_single_item(item)
            if result["success"]:
                success_count += 1
            else:
                failure_count += 1
        
        if failure_count > 0:
            self.message_user(request, f"Envios concluídos: {success_count} com sucesso, {failure_count} falharam.", messages.WARNING)
        else:
            self.message_user(request, f"{success_count} envios realizados com sucesso.", messages.SUCCESS)

    actions = ['perform_send', 'reprocess_queue', 'cancel_sending', 'mark_as_sent', 'export_logs']


