"""
Orquestrador do módulo 02. Exportações (Service Layer).

Centraliza TODA a regra de negócio: transições de estado (atômicas, anti
concorrência), enfileiramento, geração do arquivo via registry/exportadores,
atualização dos campos do registro e logging estruturado. O Admin e as tasks
do Celery apenas orquestram chamadas a este serviço — sem lógica duplicada.
"""

import logging
import time

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from domains.data_management.exceptions import (
    ExportAlreadyProcessing,
    ExportInvalidState,
    ExportPermanentFailure,
)
from domains.data_management.models import ExportModule
from domains.data_management.services.export_exporters import (
    ExportContext,
    ExportResult,
)
from domains.data_management.services.export_file_service import ExportFileService
from domains.data_management.services.export_registry import registry

logger = logging.getLogger('data_management.export')

# Estados a partir dos quais uma exportação pode ser (re)enfileirada.
ENQUEUEABLE_STATUSES = (
    ExportModule.FileStatus.PENDING,
    ExportModule.FileStatus.COMPLETED,
    ExportModule.FileStatus.FAILED,
    ExportModule.FileStatus.CANCELLED,
)
# Estados que indicam execução em andamento (proteção contra duplicidade).
RUNNING_STATUSES = (
    ExportModule.FileStatus.QUEUED,
    ExportModule.FileStatus.PROCESSING,
)


class ExportService:
    """Regras de domínio e orquestração das exportações."""

    # ------------------------------------------------------------------
    # Logging estruturado
    # ------------------------------------------------------------------
    @staticmethod
    def log_event(event, *, export_id=None, condominium_id=None,
                  service_name=None, file_format=None, task_id=None,
                  request_id=None, **extra):
        fields = {
            'event': event,
            'export_id': export_id,
            'condominium_id': condominium_id,
            'service_name': service_name,
            'file_format': file_format,
            'task_id': task_id,
            'request_id': request_id,
        }
        fields.update(extra)
        message = f'{event} export_id={export_id} condominium_id={condominium_id}'
        if service_name:
            message += f' service_name={service_name}'
        if extra.get('duration_ms') is not None:
            message += f" duration_ms={extra['duration_ms']}"
        logger.info(message, extra=fields)
        return fields

    @staticmethod
    def start_timer():
        return time.monotonic()

    # ------------------------------------------------------------------
    # Enfileiramento (Action do Admin)
    # ------------------------------------------------------------------
    @classmethod
    def enqueue(cls, export, *, user=None, request_id=None):
        """
        Valida o registro e o coloca em QUEUED (atômico).

        Levanta ExportInvalidState / ExportAlreadyProcessing /
        ExportServiceNotFound quando não é possível enfileirar.
        """
        user_id = getattr(user, 'id', None)
        if not export.is_active:
            raise ExportInvalidState(
                'Esta configuração de exportação está inativa.'
            )
        if export.file_status in RUNNING_STATUSES:
            raise ExportAlreadyProcessing(
                'Este registro já possui uma exportação em processamento.'
            )
        # Fail-fast na requisição: o serviço precisa existir no registry.
        registry.resolve(export.export_service)

        updated = ExportModule.objects.filter(
            pk=export.pk, file_status__in=ENQUEUEABLE_STATUSES
        ).update(file_status=ExportModule.FileStatus.QUEUED)
        if not updated:
            raise ExportAlreadyProcessing(
                'Este registro já possui uma exportação em processamento.'
            )
        export.refresh_from_db()
        cls.log_event(
            'export_queued',
            export_id=export.pk,
            condominium_id=export.condominium_id,
            service_name=export.export_service,
            file_format=export.file_format,
            user_id=user_id,
            request_id=request_id,
        )
        return export

    # ------------------------------------------------------------------
    # Execução (Task Celery)
    # ------------------------------------------------------------------
    @classmethod
    def run(cls, export_id, *, task_id=None, request_id=None) -> dict:
        """
        Executa (ou ignora, se já em andamento) a exportação `export_id`.

        - lock transacional (select_for_update) + transição atômica;
        - geração fora do lock;
        - falhas PERMANENTES e inesperadas marcam FAILED (a task decide retry);
        - retorna um dicionário padronizado para a task/Flower.
        """
        with transaction.atomic():
            export = ExportModule.objects.select_for_update().get(pk=export_id)
            if export.file_status == ExportModule.FileStatus.PROCESSING:
                cls.log_event(
                    'export_duplicate_ignored',
                    export_id=export.pk,
                    condominium_id=export.condominium_id,
                    service_name=export.export_service,
                    file_format=export.file_format,
                    task_id=task_id,
                    request_id=request_id,
                    reason='already_processing',
                )
                return {
                    'export_id': export.pk,
                    'status': 'skipped',
                    'reason': 'already_processing',
                }
            if not export.is_active:
                cls._fail(export, user_id=None)
                raise ExportInvalidState(
                    'Esta configuração de exportação está inativa.'
                )
            export.file_status = ExportModule.FileStatus.PROCESSING
            export.save(update_fields=['file_status', 'updated_at'])
            export_id_for_log = export.pk

        start = cls.start_timer()
        cls.log_event(
            'export_started',
            export_id=export_id_for_log,
            condominium_id=export.condominium_id,
            service_name=export.export_service,
            file_format=export.file_format,
            task_id=task_id,
            request_id=request_id,
        )
        try:
            result = cls._generate(export)
        except ExportPermanentFailure as exc:
            cls._fail(export)
            cls.log_event(
                'export_failed',
                export_id=export.pk,
                condominium_id=export.condominium_id,
                service_name=export.export_service,
                file_format=export.file_format,
                task_id=task_id,
                request_id=request_id,
                duration_ms=int((cls.start_timer() - start) * 1000),
                error_type=exc.__class__.__name__,
                permanent=True,
            )
            raise
        except Exception as exc:  # noqa: BLE001 - falha inesperada vira FAILED
            cls._fail(export)
            cls.log_event(
                'export_failed',
                export_id=export.pk,
                condominium_id=export.condominium_id,
                service_name=export.export_service,
                file_format=export.file_format,
                task_id=task_id,
                request_id=request_id,
                duration_ms=int((cls.start_timer() - start) * 1000),
                error_type=exc.__class__.__name__,
                permanent=False,
            )
            raise

        cls._complete(export, result)
        cls.log_event(
            'export_completed',
            export_id=export.pk,
            condominium_id=export.condominium_id,
            service_name=export.export_service,
            file_format=export.file_format,
            task_id=task_id,
            request_id=request_id,
            duration_ms=int((cls.start_timer() - start) * 1000),
            row_count=result.row_count,
            file_size=result.file_size,
        )
        return {
            'export_id': export.pk,
            'status': 'completed',
            'row_count': result.row_count,
            'file_name': result.file_path.name,
        }

    # ------------------------------------------------------------------
    # Geração do arquivo
    # ------------------------------------------------------------------
    @classmethod
    def _generate(cls, export) -> ExportResult:
        """Valida, remove o arquivo anterior, gera e valida o novo arquivo."""
        exporter = registry.resolve(export.export_service)  # ExportServiceNotFound
        ExportFileService.ensure_export_root()
        # Limpeza do arquivo anterior (sempre com validação de caminho).
        ExportFileService.remove_previous_file(export.file_generate)

        filename = ExportFileService.build_filename(
            export.export_service, export.file_format
        )
        destination = ExportFileService.export_root() / filename
        context = ExportContext(
            export_id=export.pk,
            condominium_id=export.condominium_id,
            file_format=export.file_format,
            destination=destination,
        )
        result = exporter.generate(context)
        ExportFileService.validate_generated_file(destination, export.file_format)
        return result

    # ------------------------------------------------------------------
    # Atualizações de estado
    # ------------------------------------------------------------------
    @classmethod
    def _complete(cls, export, result: ExportResult):
        export.file_generate = result.file_path.name
        export.generate_datetime = timezone.now()
        export.file_status = ExportModule.FileStatus.COMPLETED
        export.save(update_fields=[
            'file_generate', 'generate_datetime', 'file_status', 'updated_at',
        ])

    @classmethod
    def _fail(cls, export, *, user_id=None):
        export.file_generate = ''
        export.generate_datetime = None
        export.file_status = ExportModule.FileStatus.FAILED
        export.save(update_fields=[
            'file_generate', 'generate_datetime', 'file_status', 'updated_at',
        ])


# ---------------------------------------------------------------------------
# Timeout padrão (tarefa) — exposto para configuração da task.
# ---------------------------------------------------------------------------
EXPORT_TASK_TIMEOUT_SECONDS = getattr(
    settings, 'EXPORT_TASK_TIMEOUT_SECONDS', 600
)
EXPORT_TASK_RETRY_BACKOFF = getattr(settings, 'EXPORT_TASK_RETRY_BACKOFF', 15)