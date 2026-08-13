from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse
 
from domains.administrative.models import Bank, Infraction, BankAccount
from domains.administrative.models.circular import Circular
from domains.administrative.models.documents import Documents
from domains.administrative.models.meters import Meters
from domains.administrative.models.patrimony import Patrimony
from domains.administrative.models.budget_forecast import BudgetForecast
from domains.administrative.models.chart_of_account import ChartOfAccount
from domains.administrative.models.task import Task
from domains.administrative.models.task_history import TaskHistory
from domains.administrative.models.virtual_meeting import VirtualMeeting
from domains.administrative.models.virtual_meeting_topic import VirtualMeetingTopic
from domains.administrative.models.virtual_meeting_participant import VirtualMeetingParticipant
from domains.administrative.forms import BankForm, CircularForm, DocumentsForm, BankAccountForm, TaskForm, TaskHistoryForm
from domains.administrative.forms.virtual_meeting_form import VirtualMeetingForm
from domains.administrative.forms.virtual_meeting_topic_form import (
    VirtualMeetingTopicForm,
    VirtualMeetingTopicFormSet,
)
from domains.administrative.forms.virtual_meeting_participant_form import VirtualMeetingParticipantForm
from domains.administrative.forms.chartofaccount_form import ChartOfAccountForm
from domains.administrative.forms.infraction_form import InfractionsForm
from domains.administrative.forms.meter_form import MetersForm
from domains.administrative.forms.patrimony_form import PatrimonyForm
from domains.administrative.services.infraction_service import InfractionService
from domains.administrative.services.meter_service import MeterService
from domains.administrative.services.patrimony_service import PatrimonyService
from domains.administrative.services.tasks_service import TaskService

 
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


@admin.register(Meters)
class MeterAdmin(admin.ModelAdmin):
    form = MetersForm

    list_display = (
        "condominium",
        "meterType",
        "composition",
        "releaseDate",
        "previousValue",
        "currentValue",
        "Consumption",
        "Value",
        "is_active",
        "created_at",
    )

    list_filter = (
        "condominium",
        "meterType",
        "composition",
        "is_active",
        "releaseDate",
        "created_at",
    )

    search_fields = (
        "composition",
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
                    "releaseDate",
                    "meterType",
                    "composition",
                    "previousValue",
                    "currentValue",
                    "Consumption",
                    "Value",
                    "file",
                    "is_active",
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
            "js/meters_admin.js",
        )

    def get_queryset(self, request):
        return MeterService.get_admin_queryset()

 
@admin.register(Bank)
class BankAdmin(ExportCsvMixin, admin.ModelAdmin):
    form = BankForm
    list_display = ('compe', 'bank_name', 'is_active')
    search_fields = ('bank_name', 'compe')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Principal', {
            'fields': ('compe', 'bank_name', 'iban', 'bank_address', 'is_active')
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


@admin.register(BankAccount)
class BankAccountAdmin(ExportCsvMixin, admin.ModelAdmin):
    form = BankAccountForm

    list_display = (
        'bank',
        'condominium',
        'account_type',
        'account_name',
        'agency',
        'account_number',
        'account_digit',
        'initial_balance',
        'is_active',
        'created_at',
    )

    list_filter = (
        'bank',
        'condominium',
        'account_type',
        'is_active',
    )

    search_fields = (
        'account_name',
        'agency',
        'account_number',
        'account_digit',
        'bank__bank_name',
        'condominium__name',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    list_select_related = (
        'bank',
        'condominium',
        'account_type',
    )

    fieldsets = (
        (
            'Principal',
            {
                'fields': (
                    'bank',
                    'condominium',
                    'account_type',
                    'initial_balance',
                    'initial_balance_date',
                    'account_name',
                    'agency',
                    'account_number',
                    'account_digit',
                    'is_active',
                ),
            },
        ),
        (
            'Auditoria',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                ),
                'classes': ('collapse',),
            },
        ),
    )

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/utils.js',
            'js/bank_accounts_admin.js',
        )


@admin.register(Circular)
class CircularAdmin(admin.ModelAdmin):
    form = CircularForm
    list_display = ('title', 'release_date', 'is_active', 'connection_status')
    list_filter = ('condominium', 'is_active', 'connection_status')
    search_fields = ('title', 'circular_content')
    readonly_fields = ('created_at', 'updated_at', 'logs')
    actions = ['send_to_email_queue']
    filter_horizontal = ('condominium', 'types_residents')

    fieldsets = (
        ('Principal', {
            'fields': ('condominium', 'types_residents', 'release_date', 'title', 'circular_content', 'is_active')
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
            
            # Filter by resident types if specified
            resident_types = circular.types_residents.all()
            if resident_types.exists():
                residents = residents.filter(type_of_resident__in=resident_types)
            
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
    filter_horizontal = ('condominium', 'types_residents')

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "types_residents",
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
            
            # Filter by resident types if specified
            resident_types = infraction.types_residents.all()
            if resident_types.exists():
                residents = residents.filter(type_of_resident__in=resident_types)
            
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




@admin.register(Patrimony)
class PatrimonyAdmin(admin.ModelAdmin):
    form = PatrimonyForm

    list_display = (
        "asset_code",
        "name",
        "condominium",
        "asset_type",
        "asset_category",
        "asset_status",
        "state_condition",
        "quantity",
        "is_active",
    )

    list_filter = (
        "is_active",
        "asset_type",
        "asset_category",
        "asset_status",
        "state_condition",
        "requires_maintenance",
        "release_date",
        "acquisition_date",
    )

    search_fields = (
        "asset_code",
        "name",
        "serial_number",
        "invoice_number",
        "location",
    )

    readonly_fields = (
        "asset_code",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "condominium",
        "asset_type",
        "asset_category",
        "asset_status",
        "state_condition",
        "asset_brand",
        "maintenance_frequency",
        "responsible_person",
    )

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "release_date",
                    "asset_code",
                    "name",
                    "description",
                    "asset_type",
                    "asset_category",
                    "location",
                    "asset_status",
                    "state_condition",
                    "serial_number",
                    "asset_brand",
                    "asset_model",
                    "quantity",
                ),
            },
        ),
        (
            "Aquisições",
            {
                "fields": (
                    "acquisition_date",
                    "invoice_number",
                    "supplier",
                    "purchase_value",
                    "current_value",
                    "depreciation_rate",
                    "useful_life_months",
                    "warranty_expiration_date",
                ),
            },
        ),
        (
            "Manutenções",
            {
                "fields": (
                    "requires_maintenance",
                    "maintenance_frequency",
                    "last_maintenance_date",
                    "next_maintenance_date",
                    "maintenance_notes",
                ),
            },
        ),
        (
            "Documentos",
            {
                "fields": (
                    "main_photo",
                    "invoice_file",
                    "manual_file",
                    "warranty_file",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "responsible_person",
                    "is_active",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["generate_asset_code"]

    @admin.action(description="Gerar Código do Patrimônio")
    def generate_asset_code(self, request, queryset):
        generated = 0
        already_has_code = 0
        errors = []

        for patrimony in queryset:
            if patrimony.asset_code:
                already_has_code += 1
                continue
            try:
                PatrimonyService.generate_asset_code(patrimony)
                generated += 1
            except Exception as e:
                errors.append(str(e))

        messages_success = []
        if generated:
            messages_success.append(f"{generated} código(s) gerado(s) com sucesso.")
        if already_has_code:
            messages_success.append(f"{already_has_code} patrimônio(s) já possuía(m) código.")
        if messages_success:
            self.message_user(request, " ".join(messages_success))
        if errors:
            self.message_user(
                request,
                "Erros: " + "; ".join(errors),
                level=messages.ERROR,
            )

    class Media:
        js = (
            "js/patrimonys_admin.js",
        )

@admin.register(BudgetForecast)
class BudgetForecastAdmin(admin.ModelAdmin):
    pass

@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    form = ChartOfAccountForm
    list_display = (
        'account_code', 'account_name', 'condominium',
        'account_type', 'account_class', 'account_level',
        'status', 'is_default',
        'effective_start_date', 'effective_end_date',
    )
    list_filter = (
        'condominium', 'account_type', 'account_class',
        'status', 'account_level', 'is_default',
        'is_system_account', 'can_be_archived',
    )
    search_fields = (
        'account_code', 'account_name', 'external_reference',
        'condominium__name',
    )
    list_select_related = (
        'condominium', 'account_type', 'account_class',
        'account_group', 'account_subgroup',
        'parent_account', 'status',
    )
    autocomplete_fields = []
    readonly_fields = (
        'created_at', 'created_by', 'updated_at', 'updated_by',
        'approved_at', 'approved_by',
    )
    fieldsets = (
        ('Principal', {
            'fields': (
                'condominium', 'account_code', 'account_name',
                'account_type', 'account_level', 'account_class',
                'account_group', 'account_subgroup',
                'parent_account', 'account_description',
                'external_reference',
            ),
        }),
        ('Controle', {
            'classes': ('collapse',),
            'fields': (
                'status', 'effective_start_date', 'effective_end_date',
                'is_default', 'is_system_account', 'can_be_archived',
                'archive_reason', 'replacement_account', 'version',
            ),
        }),
        ('Auditoria', {
            'classes': ('collapse',),
            'fields': (
                'created_at', 'created_by', 'updated_at', 'updated_by',
                'approved_at', 'approved_by', 'change_reason',
            ),
        }),
    )

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/utils.js',
            'js/chartofaccount_admin.js',
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

class TaskHistoryInline(admin.TabularInline):
    model = TaskHistory
    form = TaskHistoryForm
    extra = 1
    ordering = ('-history_date', '-created_at')
    readonly_fields = ('created_by_user', 'created_at', 'updated_at')
    fields = ('history_date', 'description_history', 'created_by_user', 'created_at')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskForm
    inlines = [TaskHistoryInline]
    list_display = (
        'condominium', 'title', 'responsible_user', 'status',
        'release_date', 'estimated_completion_date',
        'is_active', 'created_at', 'updated_at',
    )
    list_filter = (
        'is_active', 'status', 'condominium',
    )
    search_fields = (
        'title', 'condominium__name',
        'responsible_user__username', 'responsible_user__email',
    )
    list_select_related = (
        'condominium', 'responsible_user', 'status',
    )
    readonly_fields = (
        'created_by_user', 'created_at', 'updated_at',
    )
    autocomplete_fields = []
    ordering = ('-created_at',)
    fieldsets = (
        ('Principal', {
            'fields': (
                'condominium', 'created_by_user', 'responsible_user',
                'title', 'release_date', 'estimated_completion_date',
                'completion_date', 'description', 'is_active', 'status',
            ),
        }),
    )
    actions = ['bulk_update_status', 'bulk_complete_tasks']

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/utils.js',
        )

    def get_changeform_initial_data(self, request):
        return {'created_by_user': request.user}

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by_user = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TaskHistory) and instance.pk is None:
                instance.created_by_user = request.user
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        return TaskService.get_admin_queryset()

    @admin.action(description='Alterar status em lote')
    def bulk_update_status(self, request, queryset):
        from django.shortcuts import render
        from django.contrib import messages
        from domains.email_service.models import ConnectionStatus

        if 'apply' in request.POST:
            new_status_id = request.POST.get('new_status')
            task_ids = request.POST.getlist('_selected_action')

            if not task_ids:
                self.message_user(request, 'Nenhuma tarefa selecionada.', level=messages.ERROR)
                return

            try:
                updated = TaskService.bulk_update_status(
                    request.user, task_ids, new_status_id,
                )
                self.message_user(
                    request,
                    f'{updated} tarefa(s) atualizada(s) com sucesso.',
                )
            except Exception as e:
                self.message_user(request, str(e), level=messages.ERROR)

            return

        status_list = ConnectionStatus.objects.filter(is_active=True)
        return render(request, 'admin/bulk_update_status.html', {
            'title': 'Alterar status em lote',
            'tasks': queryset,
            'status_list': status_list,
            'action': 'bulk_update_status',
            'opts': self.model._meta,
        })

    @admin.action(description='Baixa de tarefas')
    def bulk_complete_tasks(self, request, queryset):
        from django.shortcuts import render
        from django.contrib import messages
        from django.utils import timezone
        from domains.email_service.models import ConnectionStatus

        if 'apply' in request.POST:
            completion_date = request.POST.get('completion_date')
            new_status_id = request.POST.get('new_status')
            task_ids = request.POST.getlist('_selected_action')

            if not task_ids:
                self.message_user(request, 'Nenhuma tarefa selecionada.', level=messages.ERROR)
                return

            try:
                updated = TaskService.bulk_complete_tasks(
                    request.user, task_ids, completion_date, new_status_id,
                )
                self.message_user(
                    request,
                    f'{updated} tarefa(s) baixada(s) com sucesso.',
                )
            except Exception as e:
                self.message_user(request, str(e), level=messages.ERROR)

            return

        my_tasks = queryset.filter(created_by_user=request.user)
        status_list = ConnectionStatus.objects.filter(is_active=True)
        return render(request, 'admin/bulk_complete_tasks.html', {
            'title': 'Baixa de tarefas',
            'tasks': my_tasks,
            'status_list': status_list,
            'action': 'bulk_complete_tasks',
            'opts': self.model._meta,
        })

class VirtualMeetingTopicInline(admin.TabularInline):
    model = VirtualMeetingTopic
    form = VirtualMeetingTopicForm
    formset = VirtualMeetingTopicFormSet
    extra = 1
    fields = ('title', 'description', 'topic_options')
    verbose_name = 'Pauta'
    verbose_name_plural = 'Pautas'


class VirtualMeetingParticipantInline(admin.TabularInline):
    model = VirtualMeetingParticipant
    form = VirtualMeetingParticipantForm
    extra = 1
    fields = ('resident_type', 'resident')
    verbose_name = 'Participante'
    verbose_name_plural = 'Participantes'


@admin.register(VirtualMeeting)
class VirtualMeetingAdmin(admin.ModelAdmin):
    form = VirtualMeetingForm
    inlines = [
        VirtualMeetingTopicInline,
    ]
    jazzmin_section_order = (
        'Principal',
        'Edital de Convocação',
        'Participantes',
        'Pautas',
        'Configurações',
        'Auditoria',
    )
    list_display = (
        'title', 'condominium', 'meeting_status',
        'meeting_date_time_start', 'notice_meeting_date_time',
        'updated_at',
    )
    list_filter = (
        'meeting_status', 'condominium',
        'meeting_date_time_start',
    )
    search_fields = (
        'title', 'president', 'secretary',
        'condominium__name',
    )
    list_select_related = (
        'condominium', 'meeting_status',
    )
    readonly_fields = (
        'created_by_user_display', 'created_at', 'updated_at', 'status_assembleia',
        'email_log',
    )
    autocomplete_fields = ('condominium', 'voting_type')
    ordering = ('-created_at',)
    list_per_page = 25
    fieldsets = (
        ('Principal', {
            'fields': (
                'condominium', 'title', 'voting_type', 'location',
                'meeting_date_time_start', 'meeting_date_time_end',
                'meeting_date_time_voting_begins', 'meeting_date_time_voting_end',
                'meeting_date_time_send_mail',
                'president', 'secretary', 'video_conference_link', 'description',
            ),
        }),
        ('Edital de Convocação', {
            'classes': ('collapse',),
            'fields': (
                'notice_meeting_title', 'notice_meeting_date_time',
                'notice_meeting_description',
            ),
        }),
        ('Participantes', {
            'fields': (
                'participating_groups',
                'participating_resident',
            ),
        }),
        ('Configurações', {
            'classes': ('collapse',),
            'fields': (
                'status_assembleia',
                'email_smtp_configuration',
                'connection_status',
                'email_log',
                'notice_meeting_send_email_participants',
                'participating_vote_unit',
                'ban_those_in_default_from_voting',
                'hide_results_from_participants_during_voting',
                'release_the_agenda_for_vote',
                'allow_comments', 'show_comments',
                'allow_replies_to_comments', 'show_replies_to_comments',
            ),
        }),
        ('Auditoria', {
            'classes': ('collapse',),
            'fields': ('created_by_user_display', 'created_at', 'updated_at'),
        }),
    )
    actions = ['enviar_fila_email']

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/virtual_meeting_admin.js',
            'js/virtualmeeting_participants.js',
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'condominium', 'meeting_status',
            'email_smtp_configuration', 'connection_status',
        ).prefetch_related(
            'participating_groups', 'participating_resident',
        )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.DateTimeField):
            kwargs.pop('form_class', None)
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        self._current_user = request.user
        return super().get_readonly_fields(request, obj)

    def created_by_user_display(self, obj):
        from django.utils.html import format_html, mark_safe

        user = getattr(self, '_current_user', None)
        if user is None:
            user = obj.created_by_user if obj else None
        options = []
        for u in User.objects.all().order_by('username'):
            selected = ' selected' if user and u.pk == user.pk else ''
            options.append(f'<option value="{u.pk}"{selected}>{u.username}</option>')
        return format_html(
            '<select class="form-control" disabled>{}</select>',
            mark_safe(''.join(options)),
        )
    created_by_user_display.short_description = 'Criado por'

    def status_assembleia(self, obj):
        from domains.administrative.services.virtual_meeting_service import VirtualMeetingService

        try:
            status = VirtualMeetingService.get_pending_status()
        except Exception:
            return '-'
        return status.description if status else '-'
    status_assembleia.short_description = 'Status da assembleia'

    def save_model(self, request, obj, form, change):
        from domains.administrative.services.virtual_meeting_service import VirtualMeetingService

        try:
            if not change and obj.meeting_status_id is None:
                obj.meeting_status = VirtualMeetingService.get_pending_status()
        except Exception:
            pass
        if not change:
            user = getattr(request, 'user', None)
            if user is not None:
                obj.created_by_user = user
        super().save_model(request, obj, form, change)

    @admin.action(description='Enviar Fila E-mail')
    def enviar_fila_email(self, request, queryset):
        from django.contrib import messages
        from domains.administrative.exceptions import VirtualMeetingValidationException
        from domains.administrative.services.virtual_meeting_email_service import VirtualMeetingEmailService

        total_schedules = 0
        total_recipients = 0
        total_no_email = 0
        total_skipped = 0
        total_errors = 0

        for virtual_meeting in queryset:
            try:
                results = VirtualMeetingEmailService.schedule_emails(virtual_meeting)
                if results.get('skipped'):
                    total_skipped += 1
                    self.message_user(
                        request,
                        f"{virtual_meeting.title}: envio em massa desabilitado "
                        f"(campo 'Enviar e-mail aos participantes' = Não).",
                        level=messages.WARNING,
                    )
                    continue
                total_schedules += len(results.get('schedules', []))
                total_recipients += sum(
                    s.get('recipients', 0) for s in results.get('schedules', [])
                )
                total_no_email += results.get('no_email', 0)
                self.message_user(
                    request,
                    f"{virtual_meeting.title}: {len(results.get('schedules', []))} "
                    f"agendamento(s) criado(s) - {total_recipients} destinatário(s).",
                    level=messages.SUCCESS,
                )
            except VirtualMeetingValidationException as exc:
                total_errors += 1
                self.message_user(
                    request,
                    f'{virtual_meeting.title}: {exc}',
                    level=messages.ERROR,
                )
            except Exception as exc:
                total_errors += 1
                import logging
                logger = logging.getLogger('domains.administrative.admin')
                logger.exception(
                    'virtual_meeting_email_action_error',
                    extra={
                        'virtual_meeting_id': virtual_meeting.pk,
                        'operation': 'send_email_queue_action',
                    },
                )
                self.message_user(
                    request,
                    f'{virtual_meeting.title}: erro inesperado ({exc}).',
                    level=messages.ERROR,
                )

        summary = (
            f"Processamento concluído:\n"
            f"- Assembleias processadas: {len(queryset)}\n"
            f"- Agendamentos criados: {total_schedules}\n"
            f"- Destinatários agendados: {total_recipients}\n"
            f"- Participantes sem e-mail (ignorados): {total_no_email}\n"
            f"- Assembleias sem envio (flag desabilitado): {total_skipped}\n"
            f"- Assembleias com erro: {total_errors}\n"
            f"Consulte o campo 'Email Logs' e os agendamentos de cada registro para detalhes."
        )
        self.message_user(request, summary)

    def has_add_permission(self, request):
        return True

