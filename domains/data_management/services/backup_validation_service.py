"""
Backup validation service.

Centraliza a validação de domínio do módulo de backups: datas, caminhos e
arquivos. Nenhum comando é executado aqui; apenas validações defensivas,
reutilizáveis pelo Admin, pelas views e (futuramente) pelas tasks do Celery.
"""
import logging
import os
from pathlib import Path

from django.conf import settings

from core.services.validators import validate_date as core_validate_date
from domains.data_management.exceptions import (
    BackupFileNotFound,
    BackupValidationException,
)

logger = logging.getLogger('data_management.backup')


class BackupValidationService:
    """Validações de domínio para o módulo 01. Backups."""

    # ------------------------------------------------------------------
    # Datas
    # ------------------------------------------------------------------
    @staticmethod
    def validate_date(value):
        """Valida se `value` é uma data válida (aceita date/datetime ou str)."""
        if not core_validate_date(value):
            logger.warning(
                'backup_date_invalid',
                extra={
                    'event': 'backup_date_invalid',
                    'error_type': 'BackupValidationException',
                },
            )
            raise BackupValidationException('Data informada é inválida.')
        return value

    # ------------------------------------------------------------------
    # Caminhos / arquivos
    # ------------------------------------------------------------------
    @staticmethod
    def backup_root():
        """Diretório permitido (configurável) onde vivem os arquivos de backup."""
        return Path(settings.BACKUP_ROOT).resolve()

    @classmethod
    def _is_within_directory(cls, resolved_path, directory):
        try:
            resolved_path.is_relative_to(directory)
        except AttributeError:  # pragma: no cover - Python < 3.9
            return str(resolved_path).startswith(str(directory) + os.sep)
        return resolved_path.is_relative_to(directory)

    @classmethod
    def resolve_backup_path(cls, raw_value):
        """
        Normaliza e valida o caminho de um arquivo de backup.

        Regras:
          - vazio/URL externa => rejeitado;
          - '..' ou qualquer caminho cuja resolução saia de BACKUP_ROOT => rejeitado;
          - caminho relativo é interpretado em relação a BASE_DIR (ex.: "backups/x")
            ou a BACKUP_ROOT (ex.: "x");
          - links simbólicos são resolvidos antes da checagem de contenção, de modo
            que um symlink que aponte para fora do diretório permitido é rejeitado.
        """
        raw = (raw_value or '').strip()
        if not raw:
            raise BackupValidationException('Caminho do arquivo de backup não informado.')
        if '://' in raw:
            raise BackupValidationException('Não são permitidas URLs externas.')

        root = cls.backup_root()
        candidate = Path(raw)
        if candidate.is_absolute():
            candidates = [candidate]
        else:
            candidates = [
                Path(settings.BASE_DIR) / candidate,
                root / candidate,
            ]

        for item in candidates:
            try:
                resolved = item.resolve()
            except (OSError, RuntimeError):
                continue
            if cls._is_within_directory(resolved, root):
                return resolved

        raise BackupValidationException(
            'O caminho do arquivo está fora do diretório permitido de backups.'
        )

    @classmethod
    def validate_backup_file(cls, raw_value, *, must_exist=True):
        """
        Valida o arquivo de backup referenciado para download/restauração.

        - rejeita caminho vazio;
        - rejeita caminhos fora de BACKUP_ROOT (path traversal);
        - verifica existência, tipo regular, extensão .tar.gz e permissão de leitura.
        """
        raw = (raw_value or '').strip()
        if not raw:
            logger.warning(
                'backup_file_validation_failed',
                extra={
                    'event': 'backup_file_validation_failed',
                    'error_type': 'BackupFileNotFound',
                    'reason': 'empty_path',
                },
            )
            raise BackupFileNotFound('O download não está disponível no momento.')

        try:
            resolved = cls.resolve_backup_path(raw)
        except BackupValidationException as exc:
            logger.warning(
                'backup_file_validation_failed',
                extra={
                    'event': 'backup_file_validation_failed',
                    'error_type': exc.__class__.__name__,
                    'reason': str(exc),
                },
            )
            raise BackupFileNotFound('O download não está disponível no momento.') from exc

        if must_exist and not resolved.exists():
            logger.warning(
                'backup_file_validation_failed',
                extra={
                    'event': 'backup_file_validation_failed',
                    'error_type': 'BackupFileNotFound',
                    'reason': 'file_missing',
                },
            )
            raise BackupFileNotFound('O download não está disponível no momento.')

        if not resolved.is_file():
            logger.warning(
                'backup_file_validation_failed',
                extra={
                    'event': 'backup_file_validation_failed',
                    'error_type': 'BackupValidationException',
                    'reason': 'not_regular_file',
                },
            )
            raise BackupValidationException('O caminho informado não é um arquivo regular.')

        if resolved.suffixes and ''.join(resolved.suffixes[-2:]) != '.tar.gz':
            logger.warning(
                'backup_file_validation_failed',
                extra={
                    'event': 'backup_file_validation_failed',
                    'error_type': 'BackupValidationException',
                    'reason': 'invalid_extension',
                },
            )
            raise BackupValidationException('O arquivo de backup possui formato inválido.')

        if not os.access(str(resolved), os.R_OK):
            logger.warning(
                'backup_file_validation_failed',
                extra={
                    'event': 'backup_file_validation_failed',
                    'error_type': 'BackupValidationException',
                    'reason': 'file_not_readable',
                },
            )
            raise BackupValidationException('O arquivo de backup não pode ser lido.')

        return resolved

    # ------------------------------------------------------------------
    # Scripts de execução
    # ------------------------------------------------------------------
    @classmethod
    def validate_execution_script(cls, script_path):
        """Valida se o script autorizado existe e é executável."""
        path = Path(script_path)
        if not path.exists():
            raise BackupValidationException('O script de backup configurado não existe.')
        if not path.is_file():
            raise BackupValidationException('O script de backup configurado não é um arquivo.')
        if not os.access(str(path), os.X_OK):
            raise BackupValidationException('O script de backup configurado não é executável.')
        return path.resolve()
