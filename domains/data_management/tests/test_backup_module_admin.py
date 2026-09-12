import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import FileResponse
from django.test import Client, RequestFactory
from django.urls import reverse

from domains.data_management.admin import BackupModuleAdmin
from domains.data_management.exceptions import BackupExecutionException
from domains.data_management.forms import BackupModuleForm
from domains.data_management.models import BackupModule
from domains.data_management.services.backup_download_service import (
    BackupDownloadService,
)
from domains.data_management.services.backup_execution_service import (
    BackupExecutionService,
)
from domains.data_management.services.backup_restore_service import BackupRestoreService

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_admin(db):
    user = User.objects.create_superuser('ocpcps', 'a@b.com', 'x')
    client = Client()
    client.force_login(user)
    return client


def _admin():
    site = AdminSite()
    return BackupModuleAdmin(BackupModule, site)


def _request(factory, user=None):
    request = factory.post('/admin/data_management/backupmodule/')
    request.user = user or User.objects.create_superuser('admin')
    setattr(request, 'session', 'session')
    setattr(request, '_messages', FallbackStorage(request))
    return request


def _messages(request):
    return [m.message for m in request._messages]


def _queryset(backups):
    pks = [b.pk for b in backups]
    return BackupModule.objects.filter(pk__in=pks)


class TestBackupModuleAdminConfig:

    def test_registered(self):
        assert global_admin.site.is_registered(BackupModule)

    def test_form(self):
        assert _admin().form == BackupModuleForm

    def test_list_display(self):
        assert _admin().list_display == (
            'title', 'dateTime', 'status', 'file_url', 'is_active', 'created_at'
        )

    def test_list_filter(self):
        assert _admin().list_filter == ('status', 'is_active', 'dateTime', 'created_at')

    def test_search_fields(self):
        assert _admin().search_fields == ('title', 'description')

    def test_readonly_fields(self):
        readonly = set(_admin().readonly_fields)
        assert {'file_url', 'status', 'created_at', 'updated_at'} <= readonly

    def test_fieldsets_principal_and_auditoria(self):
        fieldsets = dict(_admin().fieldsets)
        assert 'Principal' in fieldsets
        assert 'Auditoria' in fieldsets
        principal = fieldsets['Principal']['fields']
        assert 'title' in principal
        assert 'dateTime' in principal
        assert 'file_url' in principal
        assert 'description' in principal
        assert 'is_active' in principal
        auditoria = fieldsets['Auditoria']['fields']
        assert 'status' in auditoria
        assert 'created_at' in auditoria
        assert 'updated_at' in auditoria

    def test_actions_registered(self):
        admin = _admin()
        assert admin.actions == ('execute_backup', 'download_backup', 'restore_backup')
        assert admin.execute_backup.short_description == 'Executar Backup'
        assert admin.download_backup.short_description == 'Fazer Download'
        assert admin.restore_backup.short_description == 'Executar Restaurar'

    def test_list_per_page_and_ordering(self):
        admin = _admin()
        assert admin.list_per_page == 25
        assert admin.ordering == ('-dateTime', '-created_at')


class TestBackupModuleAdminExecuteAction:

    def test_execute_skips_non_pending_and_runs_pending(self, _backup_pending, monkeypatch):
        calls = []
        done = BackupModule.objects.create(
            title='Outro Backup',
            dateTime='2026-09-01',
            status=BackupModule.Status.DONE,
        )

        def fake_execute(self, backup, *, user=None):
            calls.append(backup.pk)
            return backup

        monkeypatch.setattr(BackupExecutionService, 'execute', fake_execute)
        admin = _admin()
        request = _request(RequestFactory())
        admin.execute_backup(request, _queryset([_backup_pending, done]))
        assert calls == [_backup_pending.pk]
        assert any('não está pendente' in m for m in _messages(request))
        assert any('executado(s) com sucesso' in m for m in _messages(request))

    def test_execute_service_failure_shows_friendly_message(
        self, _backup_pending, monkeypatch
    ):
        def fake_execute(self, backup, *, user=None):
            raise BackupExecutionException('Falha na execução do script de backup.')

        monkeypatch.setattr(BackupExecutionService, 'execute', fake_execute)
        admin = _admin()
        request = _request(RequestFactory())
        admin.execute_backup(request, _queryset([_backup_pending]))
        _backup_pending.refresh_from_db()
        messages = _messages(request)
        assert any('Falha na execução do script de backup.' in m for m in messages)


class TestBackupModuleAdminRestoreAction:

    def test_restore_multiple_selection_blocked(self, monkeypatch):
        called = []
        first = BackupModule.objects.create(
            title='Backup A', dateTime='2026-09-01', status=BackupModule.Status.DONE
        )
        second = BackupModule.objects.create(
            title='Backup B', dateTime='2026-09-02', status=BackupModule.Status.DONE
        )

        def fake_restore(self, backup, *, user=None):
            called.append(backup.pk)

        monkeypatch.setattr(BackupRestoreService, 'restore', fake_restore)
        admin = _admin()
        request = _request(RequestFactory())
        admin.restore_backup(request, _queryset([first, second]))
        assert called == []
        assert any('Selecione somente um backup' in m for m in _messages(request))

    def test_restore_single_done_backup_success(self, _backup_done, monkeypatch):
        called = []

        def fake_restore(self, backup, *, user=None):
            called.append(backup.pk)
            return backup

        monkeypatch.setattr(BackupRestoreService, 'restore', fake_restore)
        admin = _admin()
        request = _request(RequestFactory())
        admin.restore_backup(request, _queryset([_backup_done]))
        assert called == [_backup_done.pk]
        assert any('concluída' in m for m in _messages(request))

    def test_restore_non_done_rejected_without_service_call(self, _backup_pending, monkeypatch):
        called = []

        def fake_restore(self, backup, *, user=None):
            called.append(backup.pk)

        monkeypatch.setattr(BackupRestoreService, 'restore', fake_restore)
        admin = _admin()
        request = _request(RequestFactory())
        admin.restore_backup(request, _queryset([_backup_pending]))
        assert called == []
        assert any('Somente backups concluídos' in m for m in _messages(request))

    def test_restore_missing_file_shows_friendly_error(self, _backup_done):
        # file_url vazio -> serviço valida antes de qualquer execução.
        admin = _admin()
        request = _request(RequestFactory())
        admin.restore_backup(request, _queryset([_backup_done]))
        assert any('Falha ao restaurar' in m for m in _messages(request))


class TestBackupModuleAdminDownloadAction:

    def test_download_multiple_selection_blocked(self, monkeypatch):
        called = []
        first = BackupModule.objects.create(title='Backup A', dateTime='2026-09-01')
        second = BackupModule.objects.create(title='Backup B', dateTime='2026-09-02')

        def fake_open(self, backup, *, user=None):
            called.append(backup.pk)

        monkeypatch.setattr(BackupDownloadService, 'open_backup_file', fake_open)
        admin = _admin()
        request = _request(RequestFactory())
        response = admin.download_backup(request, _queryset([first, second]))
        assert response is None
        assert called == []
        assert any('exatamente um backup' in m for m in _messages(request))

    def test_download_empty_file_url_shows_friendly_message(self, _backup_pending):
        admin = _admin()
        request = _request(RequestFactory())
        response = admin.download_backup(request, _queryset([_backup_pending]))
        assert response is None
        assert any('não está disponível no momento' in m for m in _messages(request))

    def test_download_valid_file_returns_streaming_response(
        self, _backup_pending, backup_root, _backup_file
    ):
        _backup_file(name='backup_mensal.tar.gz', content=b'conteudo-teste')
        _backup_pending.file_url = 'backups/backup_mensal.tar.gz'
        _backup_pending.save(update_fields=['file_url'])

        admin = _admin()
        request = _request(RequestFactory())
        response = admin.download_backup(request, _queryset([_backup_pending]))
        assert isinstance(response, FileResponse)
        assert b''.join(response.streaming_content) == b'conteudo-teste'
        assert 'attachment' in response.get('Content-Disposition', '')
        assert response.get('Content-Type') == 'application/gzip'


class TestBackupModuleAdminDownloadView:

    def _url(self, backup):
        return reverse(
            'admin:data_management_backupmodule_download', args=[backup.pk]
        )

    def test_view_streams_file(self, client_admin, _backup_pending, backup_root, _backup_file):
        _backup_file(name='backup_mensal.tar.gz', content=b'dados-do-backup')
        _backup_pending.file_url = 'backups/backup_mensal.tar.gz'
        _backup_pending.save(update_fields=['file_url'])

        response = client_admin.get(self._url(_backup_pending))
        assert response.status_code == 200
        assert b''.join(response.streaming_content) == b'dados-do-backup'
        assert 'attachment' in response.get('Content-Disposition', '')

    def test_view_404_for_missing_object(self, client_admin):
        response = client_admin.get(
            reverse('admin:data_management_backupmodule_download', args=[999999])
        )
        assert response.status_code == 404

    def test_view_404_when_file_missing(self, client_admin, _backup_pending, backup_root):
        _backup_pending.file_url = 'backups/nao_existe.tar.gz'
        _backup_pending.save(update_fields=['file_url'])
        response = client_admin.get(self._url(_backup_pending))
        assert response.status_code == 404

    def test_view_redirects_anonymous_user(self, _backup_pending):
        client = Client()
        response = client.get(self._url(_backup_pending))
        assert response.status_code in (302, 301)

    def test_view_forbids_staff_without_permission(self, _backup_pending, backup_root):
        user = User.objects.create_user('sem_perm', 'sem@perm.com', 'x')
        user.is_staff = True
        user.save()
        client = Client()
        client.force_login(user)
        response = client.get(self._url(_backup_pending))
        assert response.status_code == 403


class TestBackupModuleAdminPages:
    """Smoke test das páginas do Admin/Jazzmin do módulo."""

    def test_changelist_page_renders(self, client_admin):
        response = client_admin.get('/admin/data_management/backupmodule/')
        assert response.status_code == 200

    def test_add_page_renders(self, client_admin):
        response = client_admin.get('/admin/data_management/backupmodule/add/')
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Informe o título do backup' in content
        assert 'Principal' in content
        assert 'Auditoria' in content

    def test_change_page_renders(self, client_admin, _backup_pending):
        url = reverse(
            'admin:data_management_backupmodule_change', args=[_backup_pending.pk]
        )
        response = client_admin.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        # Status e campos técnicos não são editáveis (readonly).
        assert 'status' in content
        assert 'name="status"' not in content
        assert 'name="file_url"' not in content
