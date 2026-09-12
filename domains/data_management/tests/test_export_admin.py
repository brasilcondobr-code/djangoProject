import json

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.test import Client, RequestFactory
from django.urls import reverse

from domains.data_management.admin import ExportModuleAdmin
from domains.data_management.forms import ExportModuleForm
from domains.data_management.models import ExportModule
from domains.data_management.services.export_service import ExportService
from domains.data_management.tasks.export_tasks import run_export_task
from domains.parameters.models import TypesCondominium


@pytest.fixture
def sync_delay(monkeypatch):
    """Executa a task localmente (apply) em vez de publicar no RabbitMQ."""
    def _delay(export_id, request_id=None):
        return run_export_task.apply(args=[export_id], kwargs={'request_id': request_id})
    monkeypatch.setattr(run_export_task, 'delay', staticmethod(_delay))
    return _delay

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_admin(db):
    user = User.objects.create_superuser('ocpcps', 'a@b.com', 'x')
    client = Client()
    client.force_login(user)
    return client


def _admin():
    site = AdminSite()
    return ExportModuleAdmin(ExportModule, site)


def _request(factory, user=None):
    request = factory.post('/admin/data_management/exportmodule/')
    request.user = user or User.objects.create_superuser('admin')
    setattr(request, 'session', 'session')
    setattr(request, '_messages', FallbackStorage(request))
    return request


def _messages(request):
    return [m.message for m in request._messages]


def _queryset(exports):
    pks = [e.pk for e in exports]
    return ExportModule.objects.filter(pk__in=pks)


def _completed_export(_export, export_root):
    """Exportação concluída com arquivo real no diretório de teste."""
    TypesCondominium.objects.create(name='Admin Download')
    export = _export()
    ExportService.run(export.pk)
    export.refresh_from_db()
    return export


class TestExportModuleAdminConfig:

    def test_registered(self):
        assert global_admin.site.is_registered(ExportModule)

    def test_form(self):
        assert _admin().form == ExportModuleForm

    def test_list_display(self):
        assert _admin().list_display == (
            'condominium', 'group', 'module', 'file_format', 'export_service',
            'file_status', 'is_active', 'updated_at',
        )

    def test_list_filter(self):
        assert _admin().list_filter == (
            'condominium', 'group', 'module', 'file_format', 'file_status',
            'is_active',
        )

    def test_search_fields(self):
        assert _admin().search_fields == ('group', 'module', 'export_service')

    def test_readonly_fields(self):
        readonly = set(_admin().readonly_fields)
        assert {'generate_datetime', 'file_generate', 'file_status',
                'created_at', 'updated_at'} <= readonly

    def test_fieldsets_principal_arquivo_auditoria(self):
        fieldsets = dict(_admin().fieldsets)
        assert {'Principal', 'Arquivo', 'Auditoria'} <= set(fieldsets)
        assert 'export_service' in fieldsets['Principal']['fields']
        assert 'file_status' in fieldsets['Arquivo']['fields']

    def test_actions_registered(self):
        admin = _admin()
        assert admin.actions == ('export_data', 'download_file')
        assert admin.export_data.short_description == 'Exportar dados'
        assert admin.download_file.short_description == 'Download do arquivo'


class TestExportModuleAdminExportAction:

    def test_export_data_enqueues_and_completes(
        self, _export, export_root, sync_delay
    ):
        TypesCondominium.objects.create(name='Ação Admin')
        export = _export()
        admin = _admin()
        request = _request(RequestFactory())
        admin.export_data(request, _queryset([export]))
        export.refresh_from_db()
        # A task roda localmente (apply) — sem broker; status final Concluído.
        assert export.file_status == ExportModule.FileStatus.COMPLETED
        assert export.file_generate != ''
        assert any('enfileirada' in m for m in _messages(request))

    def test_export_data_processing_shows_warning(self, _export, sync_delay):
        export = _export(file_status=ExportModule.FileStatus.PROCESSING)
        admin = _admin()
        request = _request(RequestFactory())
        admin.export_data(request, _queryset([export]))
        assert any('já possui uma exportação em processamento' in m
                   for m in _messages(request))
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.PROCESSING

    def test_export_data_unknown_service_shows_error(self, _export):
        export = _export(export_service='nao.registrado')
        admin = _admin()
        request = _request(RequestFactory())
        admin.export_data(request, _queryset([export]))
        assert any('Falha ao enfileirar' in m for m in _messages(request))
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.PENDING


class TestExportModuleAdminDownloadAction:

    def test_download_requires_single_selection(self, _export):
        export = _export()
        other = _export(group='residents', module='units',
                        export_service='residents.units')
        admin = _admin()
        request = _request(RequestFactory())
        response = admin.download_file(request, _queryset([export, other]))
        assert response is None
        assert any('exatamente um registro' in m for m in _messages(request))

    def test_download_not_completed_shows_warning(self, _export):
        export = _export()
        admin = _admin()
        request = _request(RequestFactory())
        response = admin.download_file(request, _queryset([export]))
        assert response is None
        assert any('ainda não está pronto' in m for m in _messages(request))

    def test_download_completed_streams_file(self, _export, export_root):
        export = _completed_export(_export, export_root)
        admin = _admin()
        request = _request(RequestFactory())
        response = admin.download_file(request, _queryset([export]))
        assert response.status_code == 200
        content = b''.join(response.streaming_content)
        assert b'Admin Download' in content
        assert 'attachment' in response.get('Content-Disposition', '')
        assert response.get('Content-Type') == 'text/csv; charset=utf-8'


class TestExportModuleAdminViews:

    def test_download_view_streams(self, client_admin, _export, export_root):
        export = _completed_export(_export, export_root)
        url = reverse('admin:data_management_exportmodule_download', args=[export.pk])
        response = client_admin.get(url)
        assert response.status_code == 200
        assert b'Admin Download' in b''.join(response.streaming_content)

    def test_download_view_404_missing_file(self, client_admin, _export):
        export = _export(file_status=ExportModule.FileStatus.COMPLETED)
        url = reverse('admin:data_management_exportmodule_download', args=[export.pk])
        response = client_admin.get(url)
        assert response.status_code == 404

    def test_download_view_redirects_anonymous(self, _export):
        url = reverse('admin:data_management_exportmodule_download', args=[_export().pk])
        response = Client().get(url)
        assert response.status_code in (302, 301)

    def test_status_view_returns_json(self, client_admin, _export):
        export = _export()
        url = reverse('admin:data_management_exportmodule_status', args=[export.pk])
        response = client_admin.get(url)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['id'] == export.pk
        assert data['status'] == 'pending'
        assert data['file_name'] is None
        assert data['generated_at'] is None

    def test_status_view_after_completion(self, client_admin, _export, export_root):
        export = _completed_export(_export, export_root)
        url = reverse('admin:data_management_exportmodule_status', args=[export.pk])
        response = client_admin.get(url)
        data = json.loads(response.content)
        assert data['status'] == 'completed'
        assert data['file_name'] == export.file_generate
        assert data['generated_at'] is not None


class TestExportModuleAdminDeleteGuard:

    def test_cannot_delete_processing_record(self, _export):
        export = _export(file_status=ExportModule.FileStatus.PROCESSING)
        admin = _admin()
        assert admin.has_delete_permission(None, obj=export) is False

    def test_can_delete_completed_record(self, _export):
        export = _export(file_status=ExportModule.FileStatus.COMPLETED)
        admin = _admin()
        request = _request(RequestFactory())
        assert admin.has_delete_permission(request, obj=export) is True

    def test_delete_model_blocks_processing(self, _export):
        export = _export(file_status=ExportModule.FileStatus.QUEUED)
        admin = _admin()
        with pytest.raises(Exception):
            admin.delete_model(None, export)
        assert ExportModule.objects.filter(pk=export.pk).exists()

    def test_delete_queryset_skips_processing(self, _export):
        export = _export(file_status=ExportModule.FileStatus.PROCESSING)
        admin = _admin()
        request = _request(RequestFactory())
        admin.delete_queryset(request, _queryset([export]))
        assert ExportModule.objects.filter(pk=export.pk).exists()
        assert any('em andamento' in m for m in _messages(request))


class TestExportModuleAdminPages:

    def test_changelist_page_renders(self, client_admin, _export):
        _export()
        response = client_admin.get('/admin/data_management/exportmodule/')
        assert response.status_code == 200

    def test_add_page_renders(self, client_admin, _condominium):
        response = client_admin.get('/admin/data_management/exportmodule/add/')
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Principal' in content
        assert 'Arquivo' in content
        assert 'Auditoria' in content
        assert 'parameters.condominium_types' in content  # placeholder

    def test_change_page_renders_readonly_fields(self, client_admin, _export):
        export = _export()
        url = reverse('admin:data_management_exportmodule_change', args=[export.pk])
        response = client_admin.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="file_status"' not in content
        assert 'name="file_generate"' not in content
        assert 'name="generate_datetime"' not in content