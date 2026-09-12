"""
Serviço de download de arquivos de exportação.

Valida o registro (status Concluído), o nome do arquivo e o caminho (contenção
em EXPORT_ROOT, path traversal, existência, arquivo regular, leitura) e abre o
arquivo para streaming. Nenhuma regra de segurança depende do frontend.
"""

import logging
from pathlib import Path
from typing import BinaryIO, Tuple

from domains.data_management.exceptions import (
    ExportFileNotFound,
    ExportInvalidState,
    ExportValidationException,
)
from domains.data_management.models import ExportModule
from domains.data_management.services.export_file_service import ExportFileService
from domains.data_management.services.export_service import ExportService

logger = logging.getLogger('data_management.export')


class ExportDownloadService:
    """Disponibiliza arquivos de exportação válidos para download."""

    @staticmethod
    def open_file(export: ExportModule, *, user=None) -> Tuple[Path, BinaryIO]:
        user_id = getattr(user, 'id', None)
        if export.file_status != ExportModule.FileStatus.COMPLETED:
            ExportService.log_event(
                'export_download_failed',
                export_id=export.pk,
                user_id=user_id,
                reason='status_not_completed',
            )
            raise ExportInvalidState(
                'O arquivo ainda não está pronto para download.'
            )
        try:
            path, handle = ExportFileService.open_for_download(export.file_generate)
        except (ExportValidationException, ExportFileNotFound):
            ExportService.log_event(
                'export_download_failed',
                export_id=export.pk,
                user_id=user_id,
                reason='file_validation',
            )
            raise ExportFileNotFound(
                'O download não está disponível no momento.'
            ) from None

        ExportService.log_event(
            'export_download_started',
            export_id=export.pk,
            user_id=user_id,
            file_name=path.name,
        )
        return path, handle