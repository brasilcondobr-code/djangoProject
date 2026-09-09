import datetime
import sys

import pytest
import subprocess

from domains.data_management.exceptions import (
    BackupFileNotFound,
    BackupValidationException,
)
from domains.data_management.services.backup_command_executor import (
    BackupCommandExecutor,
    CommandResult,
)
from domains.data_management.services.backup_validation_service import (
    BackupValidationService,
)

pytestmark = pytest.mark.django_db


class TestBackupValidationServiceDates:

    def test_valid_date_object_accepted(self):
        assert BackupValidationService.validate_date(datetime.date(2026, 9, 7)) is not None

    def test_valid_string_accepted(self):
        BackupValidationService.validate_date('07/09/2026')

    def test_invalid_date_raises(self):
        with pytest.raises(BackupValidationException):
            BackupValidationService.validate_date('31/02/2026')

    def test_empty_date_raises(self):
        with pytest.raises(BackupValidationException):
            BackupValidationService.validate_date('')


class TestBackupValidationServicePaths:

    def test_empty_path_rejected(self):
        with pytest.raises(BackupValidationException):
            BackupValidationService.resolve_backup_path('')

    def test_url_rejected(self):
        with pytest.raises(BackupValidationException):
            BackupValidationService.resolve_backup_path('https://evil.com/x.tar.gz')

    def test_absolute_path_outside_root_rejected(self):
        with pytest.raises(BackupValidationException):
            BackupValidationService.resolve_backup_path('/etc/passwd')

    def test_path_traversal_rejected(self, backup_root):
        with pytest.raises(BackupValidationException):
            BackupValidationService.resolve_backup_path('../outside.tar.gz')
        with pytest.raises(BackupValidationException):
            BackupValidationService.resolve_backup_path('backups/../../outside.tar.gz')

    def test_valid_relative_path_resolves(self, backup_root, _backup_file):
        _backup_file(name='ok.tar.gz')
        resolved = BackupValidationService.resolve_backup_path('backups/ok.tar.gz')
        assert resolved == (backup_root / 'backups' / 'ok.tar.gz').resolve()

    def test_nonexistent_file_raises_download_unavailable(self, backup_root):
        with pytest.raises(BackupFileNotFound) as excinfo:
            BackupValidationService.validate_backup_file('backups/missing.tar.gz')
        assert 'não está disponível' in str(excinfo.value)

    def test_invalid_extension_rejected(self, _backup_file):
        _backup_file(name='notbackup.txt', content=b'x')
        with pytest.raises(BackupValidationException):
            BackupValidationService.validate_backup_file('backups/notbackup.txt')

    def test_directory_is_not_a_regular_file(self, backup_root):
        (backup_root / 'backups').mkdir(parents=True)
        with pytest.raises(BackupValidationException):
            BackupValidationService.validate_backup_file('backups')

    def test_valid_file_passes(self, _backup_file):
        path = _backup_file(name='valid.tar.gz', content=b'DATA')
        resolved = BackupValidationService.validate_backup_file('backups/valid.tar.gz')
        assert resolved == path.resolve()
        assert resolved.read_bytes() == b'DATA'

    def test_unreadable_file_rejected(self, _backup_file, monkeypatch):
        _backup_file(name='secret.tar.gz')
        # Simula arquivo sem permissão de leitura de forma portável.
        monkeypatch.setattr(
            'domains.data_management.services.backup_validation_service.os.access',
            lambda path, mode: False,
        )
        with pytest.raises(BackupValidationException):
            BackupValidationService.validate_backup_file('backups/secret.tar.gz')

    def test_execution_script_validation(self, backup_root):
        valid = BackupValidationService.validate_execution_script(
            str(backup_root / 'backup.sh')
        )
        assert valid == (backup_root / 'backup.sh').resolve()

        with pytest.raises(BackupValidationException):
            BackupValidationService.validate_execution_script(
                str(backup_root / 'missing.sh')
            )


class TestBackupCommandExecutor:

    def test_run_successful_command(self):
        executor = BackupCommandExecutor(timeout_seconds=5)
        result = executor.run([sys.executable, '-c', 'print("hello-backup")'])
        assert isinstance(result, CommandResult)
        assert result.returncode == 0
        assert 'hello-backup' in result.stdout

    def test_run_failing_command(self):
        executor = BackupCommandExecutor(timeout_seconds=5)
        result = executor.run([sys.executable, '-c', 'import sys; sys.exit(3)'])
        assert result.returncode == 3

    def test_run_timeout_raises(self):
        executor = BackupCommandExecutor(timeout_seconds=1)
        with pytest.raises(subprocess.TimeoutExpired):
            executor.run([sys.executable, '-c', 'import time; time.sleep(3)'])
