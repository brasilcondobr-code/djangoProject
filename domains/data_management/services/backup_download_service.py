"""
Serviço de download de backups.

Valida o arquivo referenciado (caminho vazio, path traversal, diretório
permitido, existência, arquivo regular, leitura) e o abre para streaming.
Nenhuma regra de segurança depende do frontend: toda validação é no backend.
"""
from pathlib import Path
from typing import BinaryIO, Tuple

from domains.data_management.exceptions import BackupValidationException
from domains.data_management.services.backup_service import BackupService
from domains.data_management.services.backup_validation_service import (
    BackupValidationService,
)


class BackupDownloadService:
    """Disponibiliza arquivos de backup válidos para download via streaming."""

    @staticmethod
    def open_backup_file(backup, *, user=None) -> Tuple[Path, BinaryIO]:
        """
        Valida o registro/arquivo e retorna (caminho_resolvido, handle_aberto).

        Levanta BackupValidationException/BackupFileNotFound com mensagem
        amigável quando o download não está disponível.
        """
        user_id = getattr(user, 'id', None)
        try:
            resolved = BackupValidationService.validate_backup_file(backup.file_url)
        except BackupValidationException:
            BackupService.log_event(
                'backup_download_failed',
                backup_id=backup.pk,
                user_id=user_id,
                error_type='BackupValidationException',
            )
            raise
        handle = resolved.open('rb')
        BackupService.log_event(
            'backup_download_started',
            backup_id=backup.pk,
            user_id=user_id,
            file_name=resolved.name,
        )
        return resolved, handle
