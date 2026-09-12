import uuid

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path

from .forms import BackupModuleForm, ExportModuleForm
from .models import (
    BackupModule,
    ExportModule,
    ImportModule,
    IntegrationModule,
    ScheduledTaskModule,
)
from .exceptions import (
    BackupException,
    BackupValidationException,
    ExportAlreadyProcessing,
    ExportException,
    ExportFileNotFound,
    ExportInvalidState,
    ExportValidationException,
)
from .services.backup_download_service import BackupDownloadService
from .services.backup_execution_service import BackupExecutionService
from .services.backup_restore_service import BackupRestoreService
from .services.backup_service import BackupService
from .services.export_download_service import ExportDownloadService
from .services.export_service import ExportService
from .tasks.export_tasks import run_export_task


@admin.register(ImportModule)
class ImportModuleAdmin(admin.ModelAdmin):
    pass


@admin.register(ExportModule)
class ExportModuleAdmin(admin.ModelAdmin):
    """
    Admin do módulo 02. Exportações.

    CRUD + Actions "Exportar dados" (enfileira no Celery) e
    "Download do arquivo" (streaming). Toda a lógica de negócio vive no
    Service Layer; o Admin apenas orquestra e exibe mensagens amigáveis.
    """

    form = ExportModuleForm

    list_display = (
        'condominium', 'group', 'module', 'file_format', 'export_service',
        'file_status', 'is_active', 'updated_at',
    )
    list_filter = (
        'condominium', 'group', 'module', 'file_format', 'file_status',
        'is_active',
    )
    search_fields = ('group', 'module', 'export_service')
    ordering = ('-updated_at',)
    list_per_page = 25

    readonly_fields = (
        'generate_datetime', 'file_generate', 'file_status',
        'created_at', 'updated_at',
    )
    fieldsets = (
        (
            'Principal',
            {
                'fields': (
                    'condominium', 'group', 'module', 'file_format',
                    'export_service', 'description', 'is_active',
                ),
            },
        ),
        (
            'Arquivo',
            {
                'fields': (
                    'generate_datetime', 'file_generate', 'file_status',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Auditoria',
            {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',),
            },
        ),
    )

    actions = ('export_data', 'download_file')

    # ------------------------------------------------------------------
    # Logging de auditoria de CRUD
    # ------------------------------------------------------------------
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        ExportService.log_event(
            'export_updated' if change else 'export_created',
            export_id=obj.pk,
            condominium_id=obj.condominium_id,
            service_name=obj.export_service,
            file_format=obj.file_format,
            user_id=getattr(request.user, 'id', None),
        )

    def delete_model(self, request, obj):
        if obj.file_status in (
            ExportModule.FileStatus.QUEUED,
            ExportModule.FileStatus.PROCESSING,
        ):
            raise PermissionDenied(
                'Não é possível excluir um registro com exportação em andamento.'
            )
        ExportService.log_event(
            'export_deleted',
            export_id=obj.pk,
            condominium_id=obj.condominium_id,
            user_id=getattr(request.user, 'id', None),
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        running = queryset.filter(
            file_status__in=(
                ExportModule.FileStatus.QUEUED,
                ExportModule.FileStatus.PROCESSING,
            )
        )
        if running.exists():
            self.message_user(
                request,
                'Registros com exportação em andamento não podem ser excluídos.',
                level=messages.ERROR,
            )
        deletable = queryset.exclude(
            file_status__in=(
                ExportModule.FileStatus.QUEUED,
                ExportModule.FileStatus.PROCESSING,
            )
        )
        for export in deletable:
            ExportService.log_event(
                'export_deleted',
                export_id=export.pk,
                condominium_id=export.condominium_id,
                user_id=getattr(request.user, 'id', None),
            )
        super().delete_queryset(request, deletable)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.file_status in (
            ExportModule.FileStatus.QUEUED,
            ExportModule.FileStatus.PROCESSING,
        ):
            return False
        return super().has_delete_permission(request, obj)

    # ------------------------------------------------------------------
    # Action 1 — Exportar dados
    # ------------------------------------------------------------------
    def export_data(self, request, queryset):
        enqueued = 0
        for export in queryset:
            request_id = str(uuid.uuid4())
            try:
                ExportService.enqueue(
                    export, user=request.user, request_id=request_id
                )
            except ExportAlreadyProcessing:
                self.message_user(
                    request,
                    f'"{export}" já possui uma exportação em processamento.',
                    level=messages.WARNING,
                )
                continue
            except ExportException as exc:
                self.message_user(
                    request,
                    f'Falha ao enfileirar "{export}": {exc}',
                    level=messages.ERROR,
                )
                continue
            except Exception:  # noqa: BLE001
                ExportService.log_event(
                    'export_failed',
                    export_id=export.pk,
                    condominium_id=export.condominium_id,
                    service_name=export.export_service,
                    file_format=export.file_format,
                    user_id=getattr(request.user, 'id', None),
                    error_type='UnexpectedAdminError',
                )
                self.message_user(
                    request,
                    f'Ocorreu um erro inesperado ao enfileirar "{export}". '
                    'Verifique os logs do sistema.',
                    level=messages.ERROR,
                )
                continue

            # Enfileira no Celery (RabbitMQ) — não bloqueia a requisição.
            run_export_task.delay(export.pk, request_id=request_id)
            enqueued += 1
        if enqueued:
            self.message_user(
                request,
                'A exportação foi enfileirada e será processada em segundo plano.',
                level=messages.SUCCESS,
            )

    export_data.short_description = 'Exportar dados'

    # ------------------------------------------------------------------
    # Action 2 — Download do arquivo
    # ------------------------------------------------------------------
    def download_file(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                'Selecione exatamente um registro para realizar o download.',
                level=messages.ERROR,
            )
            return None
        export = queryset.first()
        try:
            return self._build_download_response(request, export)
        except ExportInvalidState:
            self.message_user(
                request,
                'O arquivo ainda não está pronto para download.',
                level=messages.WARNING,
            )
            return None
        except (ExportValidationException, ExportFileNotFound):
            self.message_user(
                request,
                'O download não está disponível no momento.',
                level=messages.WARNING,
            )
            return None

    download_file.short_description = 'Download do arquivo'

    # ------------------------------------------------------------------
    # Views do Admin (download + status JSON)
    # ------------------------------------------------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/download/',
                self.admin_site.admin_view(self.download_view),
                name='data_management_exportmodule_download',
            ),
            path(
                '<int:object_id>/status/',
                self.admin_site.admin_view(self.status_view),
                name='data_management_exportmodule_status',
            ),
        ]
        return custom_urls + urls

    def download_view(self, request, object_id):
        """Download autenticado (staff) com validação 100% no backend."""
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied('Você não possui permissão para baixar arquivos.')
        export = get_object_or_404(ExportModule, pk=object_id)
        try:
            return self._build_download_response(request, export)
        except (ExportInvalidState, ExportValidationException, ExportFileNotFound):
            return HttpResponseNotFound('O download não está disponível no momento.')

    def status_view(self, request, object_id):
        """Retorna o status da exportação em JSON (para acompanhamento)."""
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied('Você não possui permissão para consultar.')
        export = get_object_or_404(ExportModule, pk=object_id)
        return JsonResponse({
            'id': export.pk,
            'status': export.file_status,
            'file_name': export.file_generate or None,
            'generated_at': (
                export.generate_datetime.isoformat()
                if export.generate_datetime else None
            ),
        })

    def _build_download_response(self, request, export):
        """Valida no backend e devolve FileResponse em streaming."""
        path, handle = ExportDownloadService.open_file(export, user=request.user)
        response = FileResponse(handle, as_attachment=True, filename=path.name)
        response['Content-Type'] = (
            'text/csv; charset=utf-8'
            if export.file_format == ExportModule.FileFormat.CSV
            else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        ExportService.log_event(
            'export_download_completed',
            export_id=export.pk,
            condominium_id=export.condominium_id,
            user_id=getattr(request.user, 'id', None),
            file_name=path.name,
            file_size=path.stat().st_size,
        )
        return response


@admin.register(ScheduledTaskModule)
class ScheduledTaskModuleAdmin(admin.ModelAdmin):
    list_display = (
        'virtual_meeting', 'task_type', 'scheduled_at', 'status',
        'attempts', 'sent_at',
    )
    list_filter = ('status', 'task_type', 'scheduled_at')
    search_fields = ('virtual_meeting__title',)
    readonly_fields = (
        'virtual_meeting', 'task_type', 'scheduled_at', 'status', 'attempts',
        'sent_at', 'last_error', 'celery_task_id', 'created_at', 'updated_at',
    )
    ordering = ('-scheduled_at',)
    list_per_page = 25
    list_select_related = ('virtual_meeting',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(IntegrationModule)
class IntegrationModuleAdmin(admin.ModelAdmin):
    pass


@admin.register(BackupModule)
class BackupModuleAdmin(admin.ModelAdmin):
    """
    Admin do módulo 01. Backups.

    CRUD padrão + Actions do Jazzmin (Executar Backup, Fazer Download e
    Executar Restaurar). Toda a lógica de negócio vive no Service Layer; aqui
    ficam apenas orquestração, mensagens administrativas e validações de UI.
    """

    form = BackupModuleForm

    list_display = ('title', 'dateTime', 'status', 'file_url', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'dateTime', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-dateTime', '-created_at')
    list_per_page = 25
    date_hierarchy = 'created_at'

    readonly_fields = ('file_url', 'status', 'created_at', 'updated_at')
    fieldsets = (
        (
            'Principal',
            {
                'fields': ('title', 'dateTime', 'file_url', 'description', 'is_active'),
            },
        ),
        (
            'Auditoria',
            {
                'fields': ('status', 'created_at', 'updated_at'),
                'classes': ('collapse',),
            },
        ),
    )

    actions = ('execute_backup', 'download_backup', 'restore_backup')

    # ------------------------------------------------------------------
    # Logging de auditoria de CRUD
    # ------------------------------------------------------------------
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        BackupService.log_event(
            'backup_updated' if change else 'backup_created',
            backup_id=obj.pk,
            user_id=getattr(request.user, 'id', None),
            title=obj.title,
        )

    def delete_model(self, request, obj):
        BackupService.log_event(
            'backup_deleted',
            backup_id=obj.pk,
            user_id=getattr(request.user, 'id', None),
            title=obj.title,
        )
        super().delete_model(request, obj)

    # ------------------------------------------------------------------
    # Action 1 — Executar Backup
    # ------------------------------------------------------------------
    def execute_backup(self, request, queryset):
        executed = 0
        for backup in queryset:
            if backup.status not in (
                BackupModule.Status.PENDING,
                BackupModule.Status.FAILED,
            ):
                self.message_user(
                    request,
                    f'O backup "{backup.title}" não está pendente ou com falha '
                    f'(status atual: {backup.get_status_display()}).',
                    level=messages.WARNING,
                )
                continue
            if not backup.is_active:
                self.message_user(
                    request,
                    f'O backup "{backup.title}" está inativo e não pode ser executado.',
                    level=messages.WARNING,
                )
                continue
            try:
                BackupExecutionService().execute(backup, user=request.user)
                executed += 1
            except BackupException as exc:
                # Mensagens amigáveis; detalhes ficam nos logs estruturados.
                self.message_user(
                    request,
                    f'Falha ao executar o backup "{backup.title}": {exc}',
                    level=messages.ERROR,
                )
            except Exception:  # noqa: BLE001
                BackupService.log_event(
                    'backup_execution_failed',
                    backup_id=backup.pk,
                    user_id=getattr(request.user, 'id', None),
                    error_type='UnexpectedAdminError',
                )
                self.message_user(
                    request,
                    f'Ocorreu um erro inesperado ao executar o backup "{backup.title}". '
                    f'Verifique os logs do sistema.',
                    level=messages.ERROR,
                )
        if executed:
            self.message_user(
                request,
                f'{executed} backup(s) executado(s) com sucesso.',
                level=messages.SUCCESS,
            )

    execute_backup.short_description = 'Executar Backup'

    # ------------------------------------------------------------------
    # Action 2 — Fazer Download
    # ------------------------------------------------------------------
    def download_backup(self, request, queryset):
        # Download aceita somente um arquivo por vez.
        if queryset.count() != 1:
            self.message_user(
                request,
                'Selecione exatamente um backup para realizar o download.',
                level=messages.ERROR,
            )
            return None
        backup = queryset.first()
        try:
            return self._build_download_response(request, backup)
        except BackupValidationException:
            self.message_user(
                request,
                'O download não está disponível no momento.',
                level=messages.WARNING,
            )
            return None

    download_backup.short_description = 'Fazer Download'

    # ------------------------------------------------------------------
    # Action 3 — Executar Restaurar
    # ------------------------------------------------------------------
    def restore_backup(self, request, queryset):
        # Restauração aceita SOMENTE um registro (operações destrutivas).
        if queryset.count() != 1:
            self.message_user(
                request,
                'Selecione somente um backup para realizar a restauração.',
                level=messages.ERROR,
            )
            return None
        backup = queryset.first()
        if backup.status != BackupModule.Status.DONE:
            self.message_user(
                request,
                f'Somente backups concluídos podem ser restaurados. '
                f'Status atual: {backup.get_status_display()}.',
                level=messages.ERROR,
            )
            return None
        try:
            BackupRestoreService().restore(backup, user=request.user)
            self.message_user(
                request,
                f'Restauração do backup "{backup.title}" concluída.',
                level=messages.SUCCESS,
            )
        except BackupException as exc:
            self.message_user(
                request,
                f'Falha ao restaurar o backup "{backup.title}": {exc}',
                level=messages.ERROR,
            )
        except Exception:  # noqa: BLE001
            BackupService.log_event(
                'backup_restore_failed',
                backup_id=backup.pk,
                user_id=getattr(request.user, 'id', None),
                error_type='UnexpectedAdminError',
            )
            self.message_user(
                request,
                f'Ocorreu um erro inesperado ao restaurar o backup "{backup.title}". '
                f'Verifique os logs do sistema.',
                level=messages.ERROR,
            )
        return None

    restore_backup.short_description = 'Executar Restaurar'

    # ------------------------------------------------------------------
    # Download (compartilhado entre Action e view do Admin)
    # ------------------------------------------------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/download/',
                self.admin_site.admin_view(self.download_view),
                name='data_management_backupmodule_download',
            ),
        ]
        return custom_urls + urls

    def download_view(self, request, object_id):
        """View de download dentro do Admin (autenticação/exigida pelo Admin)."""
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied('Você não possui permissão para baixar backups.')
        backup = get_object_or_404(BackupModule, pk=object_id)
        try:
            return self._build_download_response(request, backup)
        except BackupValidationException:
            return HttpResponseNotFound('O download não está disponível no momento.')

    def _build_download_response(self, request, backup):
        """Valida o arquivo no backend e devolve uma FileResponse em streaming."""
        path, handle = BackupDownloadService.open_backup_file(
            backup, user=request.user
        )
        response = FileResponse(handle, as_attachment=True, filename=path.name)
        response['Content-Type'] = 'application/gzip'
        BackupService.log_event(
            'backup_download_completed',
            backup_id=backup.pk,
            user_id=getattr(request.user, 'id', None),
            file_name=path.name,
            file_size=path.stat().st_size,
        )
        return response

