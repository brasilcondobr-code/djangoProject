"""
Abstração de execução de comandos do módulo de backups.

Responsabilidades:
  - receber comandos de forma estruturada (lista de argumentos);
  - executar SEM shell (sem concatenação de comandos);
  - aplicar timeout;
  - capturar stdout/stderr e código de retorno;
  - não expor segredos (nada de credenciais é passado aqui).

A implementação atual é síncrona (subprocess). A troca por uma execução via
Celery no futuro deve ocorrer apenas nesta camada, mantendo o Service Layer
desacoplado.
"""
import logging
import subprocess
from dataclasses import dataclass
from typing import List, Optional

from django.conf import settings

logger = logging.getLogger('data_management.backup')


@dataclass(frozen=True)
class CommandResult:
    """Resultado normalizado de uma execução."""

    returncode: int
    stdout: str
    stderr: str


class BackupCommandExecutor:
    """Executa scripts autorizados de backup/restore de forma segura."""

    def __init__(self, timeout_seconds: Optional[int] = None, *, logger_=None):
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.BACKUP_EXECUTION_TIMEOUT_SECONDS
        )
        self._logger = logger_ or logger

    def run(
        self,
        command: List[str],
        *,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> CommandResult:
        """
        Executa `command` (lista estruturada) e retorna um CommandResult.

        Nunca utiliza shell; `command[0]` deve ser um script autorizado já
        validado pelo BackupValidationService.
        """
        script = command[0] if command else '?'
        self._logger.info(
            'backup_command_started',
            extra={
                'event': 'backup_command_started',
                'script': script.rsplit('/', 1)[-1],
                'timeout_seconds': timeout or self.timeout_seconds,
            },
        )
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout or self.timeout_seconds,
            cwd=cwd,
        )
        result = CommandResult(
            returncode=completed.returncode,
            stdout=(completed.stdout or '')[:4000],
            stderr=(completed.stderr or '')[:4000],
        )
        self._logger.info(
            'backup_command_finished',
            extra={
                'event': 'backup_command_finished',
                'script': script.rsplit('/', 1)[-1],
                'exit_code': result.returncode,
            },
        )
        return result
