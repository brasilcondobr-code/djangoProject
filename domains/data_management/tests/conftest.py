import datetime

import pytest

from domains.condominium.models import Condominium
from domains.data_management.models import BackupModule, ExportModule
from domains.parameters.models import (
    Addresses,
    States,
    StructionCondominium,
    TypesCondominium,
)


@pytest.fixture
def _backup_pending(db):
    """Backup recém-criado no estado Pendente."""
    return BackupModule.objects.create(
        title='Backup Mensal',
        dateTime=datetime.date(2026, 9, 7),
    )


@pytest.fixture
def _backup_done(db, _backup_pending):
    """Backup concluído (sem arquivo associado)."""
    _backup_pending.status = BackupModule.Status.DONE
    _backup_pending.save(update_fields=['status'])
    return _backup_pending


@pytest.fixture
def backup_root(tmp_path, settings):
    """
    Diretório isolado de backups + scripts executáveis, evitando tocar no
    diretório real `backups/` do projeto e impedindo qualquer execução real.
    """
    settings.BACKUP_ROOT = tmp_path

    backup_script = tmp_path / 'backup.sh'
    backup_script.write_text('#!/bin/bash\n echo ok\n', encoding='utf-8')
    backup_script.chmod(0o755)
    settings.BACKUP_SCRIPT_PATH = str(backup_script)

    restore_script = tmp_path / 'restore.sh'
    restore_script.write_text('#!/bin/bash\n cat "$1"\n', encoding='utf-8')
    restore_script.chmod(0o755)
    settings.BACKUP_RESTORE_SCRIPT_PATH = str(restore_script)
    return tmp_path


def make_backup_file(root, name='backup_mensal.tar.gz', content=b'fake-backup-data'):
    """Cria um arquivo .tar.gz válido dentro do diretório de backups."""
    file_dir = root / 'backups'
    file_dir.mkdir(parents=True, exist_ok=True)
    path = file_dir / name
    path.write_bytes(content)
    return path


@pytest.fixture
def _backup_file(backup_root):
    """Retorna a factory que cria arquivos de backup no diretório isolado."""
    return lambda name='backup_mensal.tar.gz', content=b'fake-backup-data': make_backup_file(
        backup_root, name=name, content=content
    )


# ---------------------------------------------------------------------------
# Fixtures do módulo 02. Exportações
# ---------------------------------------------------------------------------
@pytest.fixture
def _condominium(db):
    """Condomínio mínimo para as configurações de exportação."""
    state = States.objects.create(
        name='São Paulo', abbreviation='SP', capital='São Paulo',
        region='Região Sudeste',
    )
    address = Addresses.objects.create(
        zip_code='01000-000', street='Rua A', number=10, neighborhood='Centro',
        city='São Paulo', state=state, country='Brasil',
    )
    type_cond = TypesCondominium.objects.create(name='Residencial')
    structure = StructionCondominium.objects.create(name='Padrão')
    return Condominium.objects.create(
        code='COND001', name='Condomínio Teste', cnpj='12345678000199',
        is_active=True, state_registration='123', municipal_registration='456',
        type_condominium=type_cond, struction_condominium=structure,
        address=address,
    )


@pytest.fixture
def _export(db, _condominium):
    """Factory de configurações de exportação (default: parameters.condominium_types)."""
    def factory(**overrides):
        defaults = dict(
            condominium=_condominium,
            group='parameters',
            module='condominium_types',
            file_format=ExportModule.FileFormat.CSV,
            export_service='parameters.condominium_types',
        )
        defaults.update(overrides)
        return ExportModule.objects.create(**defaults)
    return factory


@pytest.fixture
def export_root(tmp_path, settings):
    """Diretório isolado de exportações (nunca toca em media/exports real)."""
    root = tmp_path / 'exports'
    settings.EXPORT_ROOT = str(root)
    root.mkdir(parents=True, exist_ok=True)
    return root
