"""
Serviço de arquivos do módulo 02. Exportações.

Responsável por: diretório configurado (EXPORT_ROOT), nomes seguros de
arquivo, contenção de caminho (anti path traversal / symlinks), remoção segura
do arquivo anterior e validação do arquivo gerado. Nenhuma regra depende do
frontend: toda validação é feita aqui, no backend.
"""

import logging
import os
from pathlib import Path
from typing import BinaryIO, Tuple

from django.conf import settings
from django.utils import timezone

from domains.data_management.exceptions import (
    ExportFileNotFound,
    ExportValidationException,
)
from domains.data_management.services.export_validation_service import (
    FILE_PREFIX,
    ExportValidationService,
)

logger = logging.getLogger('data_management.export')


class ExportFileService:
    """Caminhos, nomes e arquivos das exportações."""

    # ------------------------------------------------------------------
    # Diretório permitido
    # ------------------------------------------------------------------
    @staticmethod
    def export_root() -> Path:
        return Path(settings.EXPORT_ROOT).resolve()

    @staticmethod
    def ensure_export_root() -> Path:
        root = ExportFileService.export_root()
        root.mkdir(parents=True, exist_ok=True)
        return root

    @classmethod
    def _is_within(cls, resolved, directory):
        try:
            return resolved.is_relative_to(directory)
        except AttributeError:  # pragma: no cover - Python < 3.9
            return str(resolved).startswith(str(directory) + os.sep)

    @classmethod
    def resolve_export_path(cls, raw_value) -> Path:
        """
        Resolve um caminho relativo de arquivo de exportação e garante que ele
        esteja DENTRO de EXPORT_ROOT (rejeita path traversal e symlinks que
        apontem para fora do diretório permitido).
        """
        raw = (raw_value or '').strip()
        if not raw:
            raise ExportValidationException('Caminho do arquivo não informado.')
        if '://' in raw:
            raise ExportValidationException('Não são permitidas URLs externas.')
        if Path(raw).is_absolute():
            raise ExportValidationException(
                'Caminhos absolutos não são aceitos para arquivos de exportação.'
            )

        root = cls.export_root()
        candidate = root / raw
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            raise ExportValidationException('Caminho do arquivo inválido.') from None
        if not cls._is_within(resolved, root):
            raise ExportValidationException(
                'O caminho do arquivo está fora do diretório permitido de exportações.'
            )
        return resolved

    # ------------------------------------------------------------------
    # Nome de arquivo seguro
    # ------------------------------------------------------------------
    @classmethod
    def build_filename(cls, service_key, file_format, *, now=None) -> str:
        """Gera `export_<service>_<ts>.<ext>` com caracteres seguros."""
        key = ExportValidationService.validate_service_key(service_key)
        ExportValidationService.validate_file_format(file_format)
        moment = now or timezone.localtime()
        timestamp = moment.strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'{FILE_PREFIX}{key}_{timestamp}.{file_format}'
        ExportValidationService.validate_filename(filename)
        if len(filename) > 250:
            raise ExportValidationException(
                'O nome do arquivo gerado excede o limite de 250 caracteres.'
            )
        return filename

    # ------------------------------------------------------------------
    # Remoção do arquivo anterior (sempre validando o caminho)
    # ------------------------------------------------------------------
    @classmethod
    def remove_previous_file(cls, file_generate):
        raw = (file_generate or '').strip()
        if not raw:
            return
        resolved = cls.resolve_export_path(raw)
        if not resolved.exists():
            # Nada a remover (arquivo já removido/volume recriado): prosseguir.
            return
        if not resolved.is_file():
            raise ExportValidationException(
                'O caminho do arquivo anterior não é um arquivo regular; '
                'remoção bloqueada.'
            )
        resolved.unlink()
        logger.info(
            'export_previous_file_removed',
            extra={'event': 'export_previous_file_removed', 'file_name': raw},
        )

    # ------------------------------------------------------------------
    # Validação do arquivo gerado
    # ------------------------------------------------------------------
    @classmethod
    def validate_generated_file(cls, path: Path, file_format) -> Path:
        resolved = path.resolve()
        root = cls.export_root()
        if not cls._is_within(resolved, root):
            raise ExportValidationException(
                'O arquivo gerado está fora do diretório permitido.'
            )
        if not resolved.exists():
            raise ExportValidationException('O arquivo gerado não existe.')
        if not resolved.is_file():
            raise ExportValidationException('O arquivo gerado não é um arquivo regular.')
        if resolved.stat().st_size <= 0:
            raise ExportValidationException('O arquivo gerado está vazio.')
        ExportValidationService.validate_extension(resolved.name, file_format)
        return resolved

    # ------------------------------------------------------------------
    # Abertura para download (streaming)
    # ------------------------------------------------------------------
    @classmethod
    def open_for_download(cls, file_generate) -> Tuple[Path, BinaryIO]:
        raw = (file_generate or '').strip()
        if not raw:
            raise ExportFileNotFound('O download não está disponível no momento.')

        try:
            resolved = cls.resolve_export_path(raw)
        except ExportValidationException:
            raise ExportFileNotFound('O download não está disponível no momento.') from None

        if not resolved.exists():
            raise ExportFileNotFound('O download não está disponível no momento.')
        if not resolved.is_file():
            raise ExportValidationException('O arquivo não é um arquivo regular.')
        if resolved.stat().st_size <= 0:
            raise ExportValidationException('O arquivo está vazio.')
        if not os.access(str(resolved), os.R_OK):
            raise ExportValidationException('O arquivo não pode ser lido.')
        return resolved, resolved.open('rb')