"""
Serviço de domínio do módulo 01. Backups.

Centraliza as transições de estado do BackupModule e o logging estruturado,
de modo que o Admin, as views e (futuramente) as tasks do Celery compartilhem
as MESMAS regras — sem lógica espalhada.
"""
import logging
import time

from domains.data_management.models import BackupModule

logger = logging.getLogger('data_management.backup')

# Estados a partir dos quais um backup pode ser (re)executado.
BACKUP_EXECUTABLE_STATUSES = (BackupModule.Status.PENDING, BackupModule.Status.FAILED)
# Estados a partir dos quais uma falha de execução/restauração pode ser marcada.
BACKUP_RUNNING_STATUSES = (
    BackupModule.Status.RUNNING,
    BackupModule.Status.RESTORING,
)


class BackupService:
    """Regras de domínio e transições de estado dos backups."""

    @staticmethod
    def log_event(event, *, backup_id=None, user_id=None, **extra):
        """Registra um evento estruturado no logger do módulo."""
        fields = {
            'event': event,
            'backup_id': backup_id,
            'user_id': user_id,
        }
        fields.update(extra)
        message = f'{event} backup_id={backup_id} user_id={user_id}'
        if extra.get('duration_ms') is not None:
            message += f" duration_ms={extra['duration_ms']}"
        logger.info(message, extra=fields)
        return fields

    @classmethod
    def transition_status(cls, backup, allowed_statuses, new_status, *, user_id=None):
        """
        Aplica uma transição de estado de forma ATÔMICA (update no banco).

        Retorna True quando aplicada. Se outro processo já tiver alterado o
        status (ex.: execução concorrente), o update não afeta linhas e a
        transição é rejeitada — prevenindo execução duplicada/corrida.
        """
        allowed = [str(value) for value in allowed_statuses]
        updated = (
            BackupModule.objects.filter(pk=backup.pk, status__in=allowed)
            .update(status=new_status)
        )
        backup.refresh_from_db()
        if updated:
            cls.log_event(
                'backup_status_changed',
                backup_id=backup.pk,
                user_id=user_id,
                old_status=','.join(allowed),
                new_status=str(new_status),
            )
            return True
        logger.warning(
            'backup_status_change_rejected',
            extra={
                'event': 'backup_status_change_rejected',
                'backup_id': backup.pk,
                'user_id': user_id,
                'current_status': backup.status,
                'required_statuses': ','.join(allowed),
            },
        )
        return False

    @classmethod
    def mark_failed(cls, backup, *, user_id=None):
        """Marca o backup como Falha caso ainda esteja em execução/restauração."""
        return cls.transition_status(
            backup, BACKUP_RUNNING_STATUSES, BackupModule.Status.FAILED, user_id=user_id
        )

    @staticmethod
    def start_timer():
        """Retorna um marcador monotônico para medir duração de operações."""
        return time.monotonic()
