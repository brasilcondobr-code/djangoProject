import datetime

import pytest

from domains.data_management.models import BackupModule


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
