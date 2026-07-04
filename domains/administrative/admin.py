from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse

from domains.administrative.models import Bank, Infraction
from domains.administrative.models.circular import Circular
from domains.administrative.models.documents import Documents
from domains.administrative.models.meter import Meter
from domains.administrative.models.notification import Notification
from domains.administrative.models.patrimony import Patrimony
from domains.administrative.models.budget_forecast import BudgetForecast
from domains.administrative.models.chart_of_account import ChartOfAccount
from domains.administrative.models.task import Task
from domains.administrative.models.virtual_assembly import VirtualAssembly
from domains.administrative.forms import BankForm, CircularForm, DocumentsForm
from domains.administrative.forms.infraction_form import InfractionsForm
from domains.administrative.services.infraction_service import InfractionService

class ExportCsvMixin:
    def init(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={self.model}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        
        writer.writerow([field.verbose_name.title() for field in self.model.fields])
        
        for obj in queryset:
            row = [getattr(obj, field) for field in self.model.fields]
            writer.writerow(row)
        return response
    
    export_as_csv.short_description = "Exportar para CSV"


@admin.register(Bank)
class BankAdmin(ExportCsvMixin, admin.ModelAdmin):
    form = BankForm
    list_display = ('compe', 'bank_name', 'agency', 'account_number', 'account_digit', 'is_active')
    search_fields = ('bank_name', 'account_number', 'iban')
    list_filter = ('account_type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Principal', {
            'fields': ('compe', 'bank_name', 'account_type', 'initial_balance', 
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
                'phone_drawn', 'email_drawn', 'addresses_drawn',
            )
        }),
        ('Gerente', {
            'fields': (
                'full_name_manager', 'phone1_manager', 'phone2_manager', 
                'phone3_manager', 'email_manager',
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
    form = CircularForm
    list_display = ('title', 'release_date', 'is_active', 'connection_status')
    list_filter = ('condominium', 'is_active', 'connection_status')
    search_fields = ('title', 'circular_content')
    readonly_fields = ('created_at', 'updated_at', 'logs')
    actions = ['send_to_email_queue']
    filter_horizontal = ('condominium',)

    fieldsets = (
        ('Principal', {
            'fields': ('condominium', 'release_date', 'title', 'circular_content', 'is_active')
        }),
        ('Configurações', {
            'fields': ('email_smtp_configuration', 'connection_status', 'logs'),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Media:
        js = (
            'js/utils.js',
            'js/custom-administrative-circular-residents-v3.js',
        )

    @admin.action(description="Enviar Fila E-mail")
    def send_to_email_queue(self, request, queryset):
        from domains.administrative.services.circular_email_queue_service import AdministrativeEmailQueueService
        from domains.residents.models import Resident
        from domains.email_service.models import ConnectionStatus
        from django.utils import timezone

        total_queued = 0
        total_residents_processed = 0
        total_no_email = 0
        total_already_queued = 0
        total_errors = 0
        skipped_invalid = 0
        skipped_no_units = 0
        skipped_no_residents = 0

        # Fetch status objects
        status_enviado = ConnectionStatus.objects.filter(status__iexact='Enviado').first()
        status_erro = ConnectionStatus.objects.filter(status__iexact='Erro').first()

        for circular in queryset:
            if not circular.title or not circular.circular_content:
                skipped_invalid += 1
                continue

            # Get all units associated with the circular
            units = circular.condominium.all()
            if not units.exists():
                skipped_no_units += 1
                continue

            # Get all residents from all selected units
            residents = Resident.objects.filter(unit__in=units)
            
            if not residents.exists():
                skipped_no_residents += 1
                continue

            res = AdministrativeEmailQueueService.queue_emails(
                entity=circular,
                residents=residents,
                module_origin="administrative_circular",
                subject=f"[Circular] {circular.title}",
                message=circular.circular_content,
                smtp_config_field='email_smtp_configuration'
            )
            total_queued += res['queued']
            total_residents_processed += res['total_residents']
            total_no_email += res['no_email']
            total_already_queued += res['already_queued']
            total_errors += res['errors']

            # Update status and logs for each circular
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            if res['errors'] > 0:
                circular.connection_status = status_erro
                log_msg = f"[{timestamp}] Erro ao processar e-mails: {res['errors']} falhas. Total residentes: {res['total_residents']}.\n"
                if circular.logs:
                    circular.logs += log_msg
                else:
                    circular.logs = log_msg
            elif res['queued'] > 0:
                circular.connection_status = status_enviado
                log_msg = f"[{timestamp}] Enviado para Filas de Envio/Email\n"
                if circular.logs:
                    circular.logs += log_msg
                else:
                    circular.logs = log_msg
            
            circular.save()

        msg = (
            f"Processamento concluído:\n"
            f"- Circulares processadas: {len(queryset) - (skipped_invalid + skipped_no_units + skipped_no_residents)}\n"
            f"- Ignoradas (conteúdo inválido): {skipped_invalid}\n"
            f"- Ignoradas (sem unidades vinculadas): {skipped_no_units}\n"
            f"- Ignoradas (unidades sem residentes): {skipped_no_residents}\n"
            f"- E-mails colocados na fila: {total_queued}\n"
            f"- Residentes com e-mail inválido/ausente: {total_no_email}\n"
            f"- E-mails já na fila: {total_already_queued}\n"
            f"- Falhas no processamento: {total_errors}\n"
            f"- Total de residentes considerados: {total_residents_processed}"
        )
        self.message_user(request, msg)


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    form = DocumentsForm

    list_display = (
        "title",
        "condominium",
        "document_type",
        "registration_date",
        "is_active",
        "created_at",
    )

    list_filter = (
        "condominium",
        "document_type",
        "is_active",
        "registration_date",
    )

    search_fields = (
        "title",
        "observations",
        "condominium__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "document_type",
                    "title",
                    "registration_date",
                    "file",
                    "observations",
                    "is_active",
                )
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

@admin.register(Infraction)
class InfractionAdmin(admin.ModelAdmin):
    form = InfractionsForm

    list_display = (
        "title",
        "infractions_type",
        "releaseDate",
        "is_active",
        "connection_status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "condominium",
        "infractions_type",
        "is_active",
        "connection_status",
        "releaseDate",
        "created_at",
    )

    search_fields = (
        "title",
        "infractionContent",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "logs",
    )
    actions = ['send_to_email_queue']
    filter_horizontal = ('condominium',)

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "releaseDate",
                    "infractions_type",
                    "title",
                    "infractionContent",
                    "file",
                    "is_active",
                ),
            },
        ),
        (
            "Configurações",
            {
                "fields": (
                    "email_smtp_configuration",
                    "connection_status",
                    "logs",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/jquery.init.js",
            "js/utils.js",
        )

    @admin.action(description="Enviar Fila E-mail")
    def send_to_email_queue(self, request, queryset):
        from domains.administrative.services.circular_email_queue_service import AdministrativeEmailQueueService
        from domains.residents.models import Resident
        from domains.email_service.models import ConnectionStatus
        from django.utils import timezone

        total_queued = 0
        total_residents_processed = 0
        total_no_email = 0
        total_already_queued = 0
        total_errors = 0
        skipped_invalid = 0
        skipped_no_units = 0
        skipped_no_residents = 0

        # Fetch status objects
        status_enviado = ConnectionStatus.objects.filter(status__iexact='Enviado').first()
        status_erro = ConnectionStatus.objects.filter(status__iexact='Erro').first()

        for infraction in queryset:
            if not infraction.title or not infraction.infractionContent:
                skipped_invalid += 1
                continue
            
            # Get all units associated with the infraction
            units = infraction.condominium.all()
            if not units.exists():
                skipped_no_units += 1
                continue

            # Get all residents from all selected units
            residents = Resident.objects.filter(unit__in=units)
            
            if not residents.exists():
                skipped_no_residents += 1
                continue

            res = AdministrativeEmailQueueService.queue_emails(
                entity=infraction,
                residents=residents,
                module_origin="administrative_infraction",
                subject=f"[Infração] {infraction.title}",
                message=infraction.infractionContent,
                smtp_config_field='email_smtp_configuration',
                attachment=infraction.file
            )
            total_queued += res['queued']
            total_residents_processed += res['total_residents']
            total_no_email += res['no_email']
            total_already_queued += res['already_queued']
            total_errors += res['errors']

            # Update status and logs for each infraction
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            if res['errors'] > 0:
                infraction.connection_status = status_erro
                log_msg = f"[{timestamp}] Erro ao processar e-mails: {res['errors']} falhas. Total residentes: {res['total_residents']}.\n"
                if infraction.logs:
                    infraction.logs += log_msg
                else:
                    infraction.logs = log_msg
            elif res['queued'] > 0:
                infraction.connection_status = status_enviado
                log_msg = f"[{timestamp}] Enviado para Filas de Envio/Email\n"
                if infraction.logs:
                    infraction.logs += log_msg
                else:
                    infraction.logs = log_msg
            
            infraction.save()

        msg = (
            f"Processamento concluído:\n"
            f"- Infrações processadas: {len(queryset) - (skipped_invalid + skipped_no_units + skipped_no_residents)}\n"
            f"- Ignoradas (conteúdo inválido): {skipped_invalid}\n"
            f"- Ignoradas (sem unidades vinculadas): {skipped_no_units}\n"
            f"- Ignoradas (unidades sem residentes): {skipped_no_residents}\n"
            f"- E-mails colocados na fila: {total_queued}\n"
            f"- Residentes com e-mail inválido/ausente: {total_no_email}\n"
            f"- E-mails já na fila: {total_already_queued}\n"
            f"- Falhas no processamento: {total_errors}\n"
            f"- Total de residentes considerados: {total_residents_processed}"
        )
        self.message_user(request, msg)


    def get_queryset(self, request):
        return InfractionService.get_admin_queryset()




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
