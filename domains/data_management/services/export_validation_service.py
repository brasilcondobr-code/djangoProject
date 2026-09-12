"""
Validações de domínio do módulo 02. Exportações.

Valida valores (formato, chave de serviço, grupo/módulo, nome de arquivo) —
sem tocar em arquivos. Validações de caminho/arquivo vivem no
ExportFileService; a regra de negócio (estados) vive no ExportService.
"""

import re

from domains.data_management.exceptions import ExportValidationException
from domains.data_management.models import ExportModule

# Caracteres seguros para chaves de serviço/nomes de arquivo (sem path traversal).
_SAFE_KEY_RE = re.compile(r'^[A-Za-z0-9._-]+$')

# Prefixo do nome padrão dos arquivos gerados.
FILE_PREFIX = 'export_'


class ExportValidationService:
    """Validações de valores do módulo de exportações."""

    # ------------------------------------------------------------------
    # Formato
    # ------------------------------------------------------------------
    @staticmethod
    def validate_file_format(value):
        allowed = ExportModule.FileFormat.values
        if value not in allowed:
            raise ExportValidationException(
                f'Formato de exportação inválido: {value!r}. '
                f'Use um destes: {", ".join(allowed)}.'
            )
        return value

    # ------------------------------------------------------------------
    # Chaves / nomes
    # ------------------------------------------------------------------
    @staticmethod
    def validate_service_key(value, *, field_label='Serviço de exportação'):
        raw = (value or '').strip()
        if not raw:
            raise ExportValidationException(f'{field_label} é obrigatório.')
        if len(raw) > 255:
            raise ExportValidationException(
                f'{field_label} deve ter no máximo 255 caracteres.'
            )
        if not _SAFE_KEY_RE.match(raw):
            raise ExportValidationException(
                f'{field_label} contém caracteres não permitidos. Use apenas '
                'letras, números, ponto, underline e hífen (ex.: '
                'parameters.condominium_types).'
            )
        return raw

    @staticmethod
    def validate_group_module(value, *, field_label):
        raw = (value or '').strip()
        if not raw:
            raise ExportValidationException(f'{field_label} é obrigatório.')
        if len(raw) > 250:
            raise ExportValidationException(
                f'{field_label} deve ter no máximo 250 caracteres.'
            )
        if not _SAFE_KEY_RE.match(raw):
            raise ExportValidationException(
                f'{field_label} contém caracteres não permitidos. Use apenas '
                'letras, números, ponto, underline e hífen (ex.: parameters).'
            )
        return raw

    # ------------------------------------------------------------------
    # Nome de arquivo
    # ------------------------------------------------------------------
    @staticmethod
    def validate_filename(value):
        """Valida um nome de arquivo relativo (sem separadores de diretório)."""
        raw = (value or '').strip()
        if not raw:
            raise ExportValidationException('Nome do arquivo não informado.')
        if '/' in raw or '\\' in raw or raw.startswith('.') or '..' in raw:
            raise ExportValidationException('Nome de arquivo inválido.')
        if not _SAFE_KEY_RE.match(raw.rsplit('.', 1)[0]) or '.' not in raw:
            raise ExportValidationException('Nome de arquivo inválido.')
        return raw

    @staticmethod
    def validate_extension(value, file_format):
        if not value.lower().endswith(f'.{file_format}'):
            raise ExportValidationException(
                f'A extensão do arquivo não corresponde ao formato {file_format}.'
            )
        return value