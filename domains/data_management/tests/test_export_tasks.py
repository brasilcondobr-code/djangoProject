import pytest

from domains.data_management.models import ExportModule
from domains.data_management.tasks.export_tasks import run_export_task
from domains.parameters.models import TypesCondominium

pytestmark = pytest.mark.django_db


class TestRunExportTask:

    def test_task_completes_export(self, _export, export_root):
        TypesCondominium.objects.create(name='Tarefa Celery')
        export = _export()
        result = run_export_task.apply(args=[export.pk]).get()
        assert result['status'] == 'completed'
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.COMPLETED
        assert export.file_generate != ''

    def test_task_marks_failed_permanent_without_retry(self, _export, export_root):
        export = _export(export_service='nao.registrado')
        result = run_export_task.apply(args=[export.pk]).get()
        assert result == {
            'export_id': export.pk,
            'status': 'failed',
            'permanent': True,
        }
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.FAILED

    def test_task_skips_when_already_processing(self, _export):
        export = _export(file_status=ExportModule.FileStatus.PROCESSING)
        result = run_export_task.apply(args=[export.pk]).get()
        assert result['status'] == 'skipped'
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.PROCESSING

    def test_duplicate_submission_is_idempotent(self, _export, export_root):
        """Enfileirar duas vezes o mesmo registro não gera duas execuções."""
        TypesCondominium.objects.create(name='Idempotência')
        export = _export()
        first = run_export_task.apply(args=[export.pk]).get()
        assert first['status'] == 'completed'
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.COMPLETED
        first_file = export.file_generate

        # Segunda submissão: estado PROCESSING/COMPLETED não gera corrida.
        export.file_status = ExportModule.FileStatus.PROCESSING
        export.save(update_fields=['file_status'])
        second = run_export_task.apply(args=[export.pk]).get()
        assert second['status'] == 'skipped'

        export.refresh_from_db()
        assert export.file_generate == first_file