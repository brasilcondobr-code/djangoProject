import subprocess

import pytest

from domains.data_management.exceptions import (
    BackupAlreadyRunning,
    BackupExecutionException,
    BackupFileNotFound,
    BackupInvalidState,
    BackupRestoreInProgress,
    BackupValidationException,
)
from domains.data_management.models import BackupModule
from domains.data_management.services.backup_command_executor import CommandResult
from domains.data_management.services.backup_download_service import (
    BackupDownloadService,
)
from domains.data_management.services.backup_execution_service import (
    BackupExecutionService,
)
from domains.data_management.services.backup_restore_service import BackupRestoreService
from domains.data_management.services.backup_service import BackupService

pytestmark = pytest.mark.django_db

SUCCESS_OUTPUT = '✅ Backup concluído: backups/backup_mensal.tar.gz'


class FakeExecutor:
    """Executor fake: nunca executa scripts reais."""

    def __init__(self, result=None, exc=None):
        self.result = result or CommandResult(returncode=0, stdout=SUCCESS_OUTPUT, stderr='')
        self.exc = exc
        self.calls = []

    def run(self, command, *, cwd=None, timeout=None):
        self.calls.append({'command': command, 'cwd': cwd, 'timeout': timeout})
        if self.exc is not None:
            raise self.exc
        return self.result


# ---------------------------------------------------------------------------
# Execução de backups
# ---------------------------------------------------------------------------
class TestBackupExecutionService:

    def test_execute_success_updates_file_url_and_status(self, _backup_pending, backup_root, _backup_file):
        _backup_file(name='backup_mensal.tar.gz')
        service = BackupExecutionService(executor=FakeExecutor())
        result = service.execute(_backup_pending)
        result.refresh_from_db()
        assert result.status == BackupModule.Status.DONE
        assert result.file_url == 'backups/backup_mensal.tar.gz'

    def test_execute_uses_configured_script_without_shell(self, _backup_pending, backup_root, _backup_file):
        _backup_file(name='backup_mensal.tar.gz')
        fake = FakeExecutor()
        BackupExecutionService(executor=fake).execute(_backup_pending)
        assert fake.calls
        command = fake.calls[0]['command']
        assert command[0] == str(backup_root / 'backup.sh')
        # Comando estruturado (lista), jamais string shell.
        assert isinstance(command, list)

    def test_execute_script_missing_keeps_pending(self, _backup_pending, backup_root):
        import django.test

        with django.test.override_settings(
            BACKUP_SCRIPT_PATH=str(backup_root / 'inexistente.sh')
        ):
            with pytest.raises(BackupExecutionException):
                BackupExecutionService(executor=FakeExecutor()).execute(_backup_pending)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.PENDING

    def test_execute_failure_returncode_marks_failed(self, _backup_pending, backup_root):
        fake = FakeExecutor(
            result=CommandResult(returncode=1, stdout='erro', stderr='boom')
        )
        with pytest.raises(BackupExecutionException):
            BackupExecutionService(executor=fake).execute(_backup_pending)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.FAILED

    def test_execute_timeout_marks_failed(self, _backup_pending, backup_root):
        fake = FakeExecutor(exc=subprocess.TimeoutExpired('backup.sh', 300))
        with pytest.raises(BackupExecutionException) as excinfo:
            BackupExecutionService(executor=fake).execute(_backup_pending)
        assert 'tempo limite' in str(excinfo.value)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.FAILED

    def test_execute_without_path_in_output_marks_failed(self, _backup_pending, backup_root):
        fake = FakeExecutor(
            result=CommandResult(returncode=0, stdout='Backup concluído sem caminho', stderr='')
        )
        with pytest.raises(BackupExecutionException):
            BackupExecutionService(executor=fake).execute(_backup_pending)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.FAILED

    def test_execute_generated_file_missing_marks_failed(self, _backup_pending, backup_root):
        # Saída aponta para arquivo que não existe no diretório permitido.
        fake = FakeExecutor()
        with pytest.raises(BackupExecutionException):
            BackupExecutionService(executor=fake).execute(_backup_pending)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.FAILED
        assert _backup_pending.file_url == ''

    def test_execute_rejects_done_backup(self, _backup_done, backup_root):
        with pytest.raises(BackupInvalidState):
            BackupExecutionService(executor=FakeExecutor()).execute(_backup_done)
        _backup_done.refresh_from_db()
        assert _backup_done.status == BackupModule.Status.DONE

    def test_execute_rejects_already_running_backup(self, _backup_pending, backup_root):
        _backup_pending.status = BackupModule.Status.RUNNING
        _backup_pending.save(update_fields=['status'])
        with pytest.raises(BackupAlreadyRunning):
            BackupExecutionService(executor=FakeExecutor()).execute(_backup_pending)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.RUNNING

    def test_execute_rejects_inactive_backup(self, _backup_pending, backup_root):
        _backup_pending.is_active = False
        _backup_pending.save(update_fields=['is_active'])
        with pytest.raises(BackupInvalidState):
            BackupExecutionService(executor=FakeExecutor()).execute(_backup_pending)

    def test_concurrent_execution_is_prevented(self, _backup_pending, backup_root, _backup_file):
        """
        Duas execuções simultâneas do MESMO registro: somente a primeira
        transiciona Pendente -> Em Execução; a segunda falha.
        """
        _backup_file(name='backup_mensal.tar.gz')
        second = FakeExecutor()

        # Simula a primeira execução já iniciada (estado Em Execução no banco).
        BackupService.transition_status(
            _backup_pending,
            [BackupModule.Status.PENDING, BackupModule.Status.FAILED],
            BackupModule.Status.RUNNING,
        )
        _backup_pending.refresh_from_db()
        with pytest.raises(BackupAlreadyRunning):
            BackupExecutionService(executor=second).execute(_backup_pending)
        assert not second.calls


# ---------------------------------------------------------------------------
# Restauração de backups
# ---------------------------------------------------------------------------
class TestBackupRestoreService:

    def test_restore_success(self, _backup_pending, backup_root, _backup_file):
        _backup_pending.status = BackupModule.Status.DONE
        _backup_pending.file_url = 'backups/backup_mensal.tar.gz'
        _backup_pending.save(update_fields=['status', 'file_url'])
        _backup_file(name='backup_mensal.tar.gz')

        fake = FakeExecutor(result=CommandResult(returncode=0, stdout='ok', stderr=''))
        BackupRestoreService(executor=fake).restore(_backup_pending)

        assert fake.calls
        command = fake.calls[0]['command']
        assert command[0] == str(backup_root / 'restore.sh')
        assert command[1].endswith('backup_mensal.tar.gz')

        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.DONE

    def test_restore_requires_done_status(self, _backup_pending, backup_root, _backup_file):
        _backup_file(name='backup_mensal.tar.gz')
        _backup_pending.file_url = 'backups/backup_mensal.tar.gz'
        _backup_pending.save(update_fields=['file_url'])
        with pytest.raises(BackupInvalidState):
            BackupRestoreService(executor=FakeExecutor()).restore(_backup_pending)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.PENDING

    def test_restore_without_file_rejected(self, _backup_done, backup_root):
        with pytest.raises(BackupInvalidState):
            BackupRestoreService(executor=FakeExecutor()).restore(_backup_done)
        _backup_done.refresh_from_db()
        assert _backup_done.status == BackupModule.Status.DONE

    def test_restore_with_missing_file_rejected(self, _backup_pending, backup_root):
        _backup_pending.status = BackupModule.Status.DONE
        _backup_pending.file_url = 'backups/nao_existe.tar.gz'
        _backup_pending.save(update_fields=['status', 'file_url'])
        with pytest.raises(BackupInvalidState):
            BackupRestoreService(executor=FakeExecutor()).restore(_backup_pending)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.DONE

    def test_restore_blocked_when_another_restore_in_progress(
        self, _backup_pending, backup_root, _backup_file
    ):
        _backup_file(name='backup_mensal.tar.gz')
        _backup_pending.status = BackupModule.Status.DONE
        _backup_pending.file_url = 'backups/backup_mensal.tar.gz'
        _backup_pending.save(update_fields=['status', 'file_url'])

        another = BackupModule.objects.create(
            title='Outro backup',
            dateTime='2026-09-06',
            status=BackupModule.Status.RESTORING,
        )
        with pytest.raises(BackupRestoreInProgress):
            BackupRestoreService(executor=FakeExecutor()).restore(_backup_pending)

    def test_restore_failure_marks_failed(self, _backup_pending, backup_root, _backup_file):
        _backup_pending.status = BackupModule.Status.DONE
        _backup_pending.file_url = 'backups/backup_mensal.tar.gz'
        _backup_pending.save(update_fields=['status', 'file_url'])
        _backup_file(name='backup_mensal.tar.gz')

        fake = FakeExecutor(result=CommandResult(returncode=1, stdout='', stderr='erro'))
        with pytest.raises(BackupExecutionException):
            BackupRestoreService(executor=fake).restore(_backup_pending)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.FAILED

    def test_restore_timeout_marks_failed(self, _backup_pending, backup_root, _backup_file):
        _backup_pending.status = BackupModule.Status.DONE
        _backup_pending.file_url = 'backups/backup_mensal.tar.gz'
        _backup_pending.save(update_fields=['status', 'file_url'])
        _backup_file(name='backup_mensal.tar.gz')

        fake = FakeExecutor(exc=subprocess.TimeoutExpired('restore.sh', 600))
        with pytest.raises(BackupExecutionException) as excinfo:
            BackupRestoreService(executor=fake).restore(_backup_pending)
        assert 'tempo limite' in str(excinfo.value)
        _backup_pending.refresh_from_db()
        assert _backup_pending.status == BackupModule.Status.FAILED

    def test_restore_rejects_inactive_backup(self, _backup_done, backup_root):
        _backup_done.is_active = False
        _backup_done.save(update_fields=['is_active'])
        with pytest.raises(BackupInvalidState):
            BackupRestoreService(executor=FakeExecutor()).restore(_backup_done)


# ---------------------------------------------------------------------------
# Download de backups
# ---------------------------------------------------------------------------
class TestBackupDownloadService:

    def test_download_valid_file(self, _backup_pending, backup_root, _backup_file):
        _backup_pending.file_url = 'backups/backup_mensal.tar.gz'
        _backup_pending.save(update_fields=['file_url'])
        _backup_file(name='backup_mensal.tar.gz', content=b'conteudo-do-backup')

        path, handle = BackupDownloadService.open_backup_file(_backup_pending)
        assert handle.read() == b'conteudo-do-backup'
        handle.close()
        assert path.name == 'backup_mensal.tar.gz'

    def test_download_empty_file_url(self, _backup_pending):
        with pytest.raises(BackupFileNotFound):
            BackupDownloadService.open_backup_file(_backup_pending)

    def test_download_file_outside_allowed_dir(self, _backup_pending):
        _backup_pending.file_url = '../../../etc/passwd'
        _backup_pending.save(update_fields=['file_url'])
        with pytest.raises(BackupFileNotFound):
            BackupDownloadService.open_backup_file(_backup_pending)
