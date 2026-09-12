"""
Serviço de execução de backups.

Orquestra a execução do script autorizado de backup (settings.BACKUP_SCRIPT_PATH):
valida o script, transiciona o status de forma atômica (anti-concorrência),
executa sem shell, valida o arquivo gerado dentro de BACKUP_ROOT e atualiza o
registro. Pronto para ser acionado de forma assíncrona (Celery) no futuro.
"""
import re
import subprocess

from django.conf import settings

from domains.data_management.exceptions import (
    BackupAlreadyRunning,
    BackupExecutionException,
    BackupInvalidState,
    BackupValidationException,
)
from domains.data_management.models import BackupModule
from domains.data_management.services.backup_command_executor import (
    BackupCommandExecutor,
    CommandResult,
)
from domains.data_management.services.backup_service import (
    BACKUP_EXECUTABLE_STATUSES,
    BackupService,
)
from domains.data_management.services.backup_validation_service import (
    BackupValidationService,
)

_BACKUP_FILE_PATTERN = re.compile(r'([A-Za-z0-9_./\-]+\.tar\.gz)')


class BackupExecutionService:
    """Executa o processo de backup e reflete o resultado no registro."""

    def __init__(self, executor=None):
        self.executor = executor or BackupCommandExecutor(
            timeout_seconds=settings.BACKUP_EXECUTION_TIMEOUT_SECONDS
        )

    def execute(self, backup, *, user=None):
        """
        Executa o backup do registro `backup`.

        Fluxo:
          1. valida o script configurado;
          2. transiciona Pendente/Falha -> Em Execução (atômico);
          3. executa o script (sem shell, com timeout);
          4. localiza o caminho do arquivo gerado na saída do script;
          5. valida o arquivo (existência + diretório permitido);
          6. grava file_url e conclui — ou marca Falha em caso de erro.
        """
        user_id = getattr(user, 'id', None)
        start = BackupService.start_timer()

        # 1. Script autorizado/configurado
        try:
            script = BackupValidationService.validate_execution_script(
                settings.BACKUP_SCRIPT_PATH
            )
        except BackupValidationException as exc:
            raise BackupExecutionException(str(exc)) from exc

        # 2. Guarda anti-concorrência: somente Pendente/Falha iniciam execução.
        if not backup.is_active:
            raise BackupInvalidState(
                'O backup está inativo e não pode ser executado.'
            )
        if backup.status in (
            BackupModule.Status.RUNNING,
            BackupModule.Status.RESTORING,
        ):
            raise BackupAlreadyRunning(
                'Este backup já está em execução. Aguarde a conclusão.'
            )
        if backup.status not in BACKUP_EXECUTABLE_STATUSES:
            raise BackupInvalidState(
                'O backup não pode ser executado a partir do estado atual '
                f'({backup.get_status_display()}).'
            )

        # Transição ATÔMICA (update condicional) — proteção contra corrida:
        # se outro processo alterou o estado entre a leitura e o update, a
        # transição é rejeitada e a execução não acontece em duplicidade.
        if not BackupService.transition_status(
            backup,
            BACKUP_EXECUTABLE_STATUSES,
            BackupModule.Status.RUNNING,
            user_id=user_id,
        ):
            raise BackupAlreadyRunning(
                'Não foi possível iniciar o backup: outro processo pode já ' 
                'estar executando este registro.'
            )

        BackupService.log_event(
            'backup_execution_started',
            backup_id=backup.pk,
            user_id=user_id,
        )

        try:
            # 3. Execução segura (lista estruturada, sem shell).
            try:
                result = self.executor.run([str(script)], cwd=str(settings.BASE_DIR))
            except (subprocess.TimeoutExpired, TimeoutError):
                raise BackupExecutionException(
                    'O backup excedeu o tempo limite de execução configurado.'
                ) from None

            # 4/5. Saída do script -> caminho do arquivo gerado.
            if result.returncode != 0:
                raise BackupExecutionException(
                    'Falha na execução do script de backup. Verifique os logs do sistema.'
                )

            raw_path = self._extract_backup_path(result)
            if not raw_path:
                raise BackupExecutionException(
                    'Backup concluído, mas não foi possível identificar o arquivo gerado.'
                )

            try:
                resolved = BackupValidationService.validate_backup_file(raw_path)
            except BackupValidationException as exc:
                raise BackupExecutionException(
                    'Backup concluído, mas o arquivo gerado é inválido.'
                ) from exc

            # 6. Persistência do resultado.
            file_url = raw_path
            file_size = resolved.stat().st_size
            updated = BackupModule.objects.filter(
                pk=backup.pk, status=BackupModule.Status.RUNNING
            ).update(status=BackupModule.Status.DONE, file_url=file_url)
            if not updated:
                raise BackupExecutionException(
                    'O estado do backup mudou durante a execução; resultado descartado.'
                )
            backup.refresh_from_db()
            BackupService.log_event(
                'backup_execution_completed',
                backup_id=backup.pk,
                user_id=user_id,
                duration_ms=int((BackupService.start_timer() - start) * 1000),
                exit_code=result.returncode,
                file_size=file_size,
            )
            return backup

        except BackupExecutionException as exc:
            BackupService.mark_failed(backup, user_id=user_id)
            BackupService.log_event(
                'backup_execution_failed',
                backup_id=backup.pk,
                user_id=user_id,
                duration_ms=int((BackupService.start_timer() - start) * 1000),
                error_type=exc.__class__.__name__,
            )
            raise

        except Exception as exc:  # noqa: BLE001 - falha inesperada deve virar Falha
            BackupService.mark_failed(backup, user_id=user_id)
            BackupService.log_event(
                'backup_execution_failed',
                backup_id=backup.pk,
                user_id=user_id,
                error_type=exc.__class__.__name__,
            )
            raise BackupExecutionException(
                'Ocorreu um erro inesperado durante a execução do backup.'
            ) from exc

    @staticmethod
    def _extract_backup_path(result: CommandResult):
        """Extrai o caminho do .tar.gz gerado a partir de stdout/stderr."""
        output = f'{result.stdout}\n{result.stderr}'
        for match in _BACKUP_FILE_PATTERN.findall(output):
            candidate = match.strip()
            if not candidate:
                continue
            try:
                resolved = BackupValidationService.resolve_backup_path(candidate)
                if resolved.is_file():
                    return candidate
            except BackupValidationException:
                continue
        return None
