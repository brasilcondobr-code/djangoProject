"""
Tasks Celery do módulo 02. Exportações.

A Action do Admin apenas valida e enfileira (ExportService.enqueue) e dispara
`run_export_task.delay(...)` — a geração acontece aqui, em segundo plano
(RabbitMQ/Celery), com monitoramento pelo Flower.

Política de retry (apenas erros TRANSITÓRIOS):
  - ExportPermanentFailure (serviço inexistente, validação, caminho inválido,
    formato inválido) -> marca FAILED e encerra, SEM retry;
  - demais exceções (banco/arquivo transitórios) -> retry com backoff;
  - a duplicidade é protegida no banco (select_for_update + status), portanto
    retries jamais criam arquivos inconsistentes.
"""

import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError, Retry

from domains.data_management.exceptions import ExportPermanentFailure
from domains.data_management.services.export_service import ExportService

logger = logging.getLogger('data_management.export')


@shared_task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
    autoretry_for=(),
)
def run_export_task(self, export_id, request_id=None):
    """
    Executa a exportação de `export_id` em segundo plano.

    Retorna dicionário padronizado:
      {'export_id': ..., 'status': 'completed' | 'failed' | 'skipped', ...}
    """
    try:
        return ExportService.run(
            export_id,
            task_id=self.request.id,
            request_id=request_id,
        )
    except ExportPermanentFailure as exc:
        # Falha definitiva: o serviço já marcou FAILED; não há retry útil.
        logger.info(
            'export_task_permanent_failure',
            extra={
                'event': 'export_task_permanent_failure',
                'export_id': export_id,
                'task_id': self.request.id,
                'error_type': exc.__class__.__name__,
            },
        )
        return {
            'export_id': export_id,
            'status': 'failed',
            'permanent': True,
        }
    except (Retry, MaxRetriesExceededError):
        raise
    except Exception as exc:  # noqa: BLE001 - erro transitório: retry com backoff
        logger.warning(
            'export_task_transient_error',
            extra={
                'event': 'export_task_transient_error',
                'export_id': export_id,
                'task_id': self.request.id,
                'error_type': exc.__class__.__name__,
            },
        )
        raise self.retry(exc=exc)