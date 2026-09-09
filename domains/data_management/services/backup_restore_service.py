"""
Serviço de restauração de backups.

Restauração é uma operação destrutiva: exige exatamente UM registro com arquivo
válido, impede restauração simultânea, transiciona o status de forma atômica e
executa o script autorizado (settings.BACKUP_RESTORE_SCRIPT_PATH) sem shell.
"""
import subprocess

from django.conf import settings

from domains.data_management.exceptions import (
    BackupAlreadyRunning,
    BackupExecutionException,
    BackupInvalidState,
    BackupRestoreInProgress,
    BackupValidationException,
)
from domains.data_management.models import BackupModule
from domains.data_management.services.backup_command_executor import (
    BackupCommandExecutor,
)
from domains.data_management.services.backup_service import BackupService
from domains.data_management.services.backup_validation_service import (
    BackupValidationService,
)


class BackupRestoreService:
    """Executa a restauração de um único backup válido."""

    def __init__(self, executor=None):
        self.executor = executor or BackupCommandExecutor(
            timeout_seconds=settings.BACKUP_RESTORE_TIMEOUT_SECONDS
        )

    def restore(self, backup, *, user=None):
        """
        Restaura o backup referenciado por `backup`.

        Regras de segurança:
          - o registro precisa estar Concluído e ativo;
          - o arquivo precisa existir, ser legível e estar em BACKUP_ROOT;
          - não pode haver outra restauração em andamento;
          - a transição para Restaurando é atômica (anti-concorrência).
        """
        user_id = getattr(user, 'id', None)
        start = BackupService.start_timer()

        if not backup.is_active:
            raise BackupInvalidState('O backup está inativo e não pode ser restaurado.')

        if backup.status != BackupModule.Status.DONE:
            raise BackupInvalidState(
                'Somente backups concluídos podem ser restaurados. '
                f'Status atual: {backup.get_status_display()}.'
            )

        if BackupModule.objects.filter(
            status=BackupModule.Status.RESTORING
        ).exclude(pk=backup.pk).exists():
            raise BackupRestoreInProgress(
                'Já existe uma restauração em andamento. Aguarde a conclusão.'
            )

        try:
            script = BackupValidationService.validate_execution_script(
                settings.BACKUP_RESTORE_SCRIPT_PATH
            )
        except BackupValidationException as exc:
            raise BackupExecutionException(str(exc)) from exc

        # Valida o arquivo ANTES de marcar Restaurando.
        try:
            backup_path = BackupValidationService.validate_backup_file(backup.file_url)
        except BackupValidationException as exc:
            raise BackupInvalidState(
                'O arquivo de backup não está disponível para restauração.'
            ) from exc

        # Transição atômica DONE -> Restaurando (anti-concorrência).
        if not BackupService.transition_status(
            backup, [BackupModule.Status.DONE], BackupModule.Status.RESTORING, user_id=user_id
        ):
            raise BackupAlreadyRunning(
                'Não foi possível iniciar a restauração: o estado do registro '
                'mudou ou já existe uma restauração em andamento.'
            )

        BackupService.log_event(
            'backup_restore_started',
            backup_id=backup.pk,
            user_id=user_id,
        )

        try:
            try:
                result = self.executor.run(
                    [str(script), str(backup_path)],
                    cwd=str(settings.BASE_DIR),
                    timeout=settings.BACKUP_RESTORE_TIMEOUT_SECONDS,
                )
            except (subprocess.TimeoutExpired, TimeoutError):
                raise BackupExecutionException(
                    'A restauração excedeu o tempo limite de execução configurado.'
                ) from None

            if result.returncode != 0:
                raise BackupExecutionException(
                    'Falha na execução do script de restauração. '
                    'Nenhum dado foi alterado ou a operação foi cancelada.'
                )

            updated = BackupModule.objects.filter(
                pk=backup.pk, status=BackupModule.Status.RESTORING
            ).update(status=BackupModule.Status.DONE)
            if not updated:
                raise BackupExecutionException(
                    'O estado do backup mudou durante a restauração; '
                    'resultado descartado.'
                )
            backup.refresh_from_db()
            BackupService.log_event(
                'backup_restore_completed',
                backup_id=backup.pk,
                user_id=user_id,
                duration_ms=int((BackupService.start_timer() - start) * 1000),
                exit_code=result.returncode,
            )
            return backup

        except BackupExecutionException as exc:
            BackupService.mark_failed(backup, user_id=user_id)
            BackupService.log_event(
                'backup_restore_failed',
                backup_id=backup.pk,
                user_id=user_id,
                duration_ms=int((BackupService.start_timer() - start) * 1000),
                error_type=exc.__class__.__name__,
            )
            raise

        except Exception as exc:  # noqa: BLE001 - falha inesperada vira Falha
            BackupService.mark_failed(backup, user_id=user_id)
            BackupService.log_event(
                'backup_restore_failed',
                backup_id=backup.pk,
                user_id=user_id,
                error_type=exc.__class__.__name__,
            )
            raise BackupExecutionException(
                'Ocorreu um erro inesperado durante a restauração.'
            ) from exc
