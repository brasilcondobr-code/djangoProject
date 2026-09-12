import zipfile
from pathlib import Path

import pytest
from django.utils import timezone

from domains.data_management.exceptions import (
    ExportAlreadyProcessing,
    ExportFileNotFound,
    ExportInvalidState,
    ExportServiceNotFound,
    ExportValidationException,
)
from domains.data_management.models import ExportModule
from domains.data_management.services.export_download_service import (
    ExportDownloadService,
)
from domains.data_management.services.export_exporters import ExportContext
from domains.data_management.services.export_file_service import ExportFileService
from domains.data_management.services.export_registry import registry
from domains.data_management.services.export_service import ExportService
from domains.data_management.services.export_validation_service import (
    ExportValidationService,
)
from domains.data_management.services.export_writers import (
    CsvExportWriter,
    XlsxExportWriter,
    get_writer,
)
from domains.parameters.models import TypesCondominium

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
class TestExportRegistry:

    def test_default_services_registered(self):
        for key in (
            'parameters.condominium_types',
            'parameters.condominium_structures',
            'parameters.states',
            'condominium.condominiums',
            'condominium.collaborators',
            'residents.units',
            'residents.residents',
            'residents.vehicles',
        ):
            assert registry.is_registered(key), key

    def test_resolve_known_service(self):
        exporter = registry.resolve('parameters.condominium_types')
        assert exporter.service_key == 'parameters.condominium_types'

    def test_resolve_unknown_service_raises(self):
        with pytest.raises(ExportServiceNotFound):
            registry.resolve('nao.existe.no.registro')

    def test_resolve_never_executes_arbitrary_code(self, monkeypatch):
        """O registry NÃO importa código a partir do texto informado."""
        import builtins

        calls = []
        original = builtins.__import__

        def fake_import(name, *args, **kwargs):
            calls.append(name)
            return original(name, *args, **kwargs)

        monkeypatch.setattr(builtins, '__import__', fake_import)
        with pytest.raises(ExportServiceNotFound):
            registry.resolve('os.system')
        assert 'os' not in calls


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------
class TestExportWriters:

    def test_csv_writer_creates_file(self, tmp_path):
        dest = tmp_path / 'out.csv'
        count = CsvExportWriter().write(
            ['Nome', 'Ativo'], [['A', 'Sim'], ['B', 'Não']], dest
        )
        assert count == 2
        content = dest.read_bytes()
        assert content.startswith(b'\xef\xbb\xbf')  # BOM (Excel)
        text = dest.read_text(encoding='utf-8-sig')
        assert text.splitlines()[0] == 'Nome;Ativo'
        assert 'A;Sim' in text

    def test_csv_handles_special_characters(self, tmp_path):
        dest = tmp_path / 'out.csv'
        CsvExportWriter().write(
            ['Campo'], [['texto;com;ponto-e-vírgula'], ['vírgula, e "aspas"']], dest
        )
        text = dest.read_text(encoding='utf-8-sig')
        assert 'texto;com;ponto-e-vírgula' in text  # campo não contém ';' literal
        assert '"aspas"' in text

    def test_xlsx_writer_creates_valid_zip(self, tmp_path):
        dest = tmp_path / 'out.xlsx'
        count = XlsxExportWriter().write(
            ['Nome', 'Qtde'],
            [['Item A', '3'], ['Item B', '10.5']],
            dest,
        )
        assert count == 2
        with zipfile.ZipFile(dest) as zf:
            assert '[Content_Types].xml' in zf.namelist()
            assert 'xl/worksheets/sheet1.xml' in zf.namelist()
            sheet = zf.read('xl/worksheets/sheet1.xml').decode('utf-8')
        assert '<row r="1">' in sheet      # cabeçalho
        assert 'Item A' in sheet
        assert 'Item B' in sheet
        assert '<v>3</v>' in sheet         # numérico tipado
        assert 'xml:space="preserve"' in sheet

    def test_get_writer_unknown_format(self):
        with pytest.raises(ExportValidationException):
            get_writer('pdf')


# ---------------------------------------------------------------------------
# Validações
# ---------------------------------------------------------------------------
class TestExportValidationService:

    def test_valid_file_format(self):
        assert ExportValidationService.validate_file_format('csv') == 'csv'
        assert ExportValidationService.validate_file_format('xlsx') == 'xlsx'

    def test_invalid_file_format(self):
        with pytest.raises(ExportValidationException):
            ExportValidationService.validate_file_format('pdf')

    def test_service_key_safe_chars(self):
        assert ExportValidationService.validate_service_key(
            'parameters.condominium_types'
        ) == 'parameters.condominium_types'

    def test_service_key_rejects_traversal(self):
        with pytest.raises(ExportValidationException):
            ExportValidationService.validate_service_key('../etc/passwd')

    def test_group_module_rules(self):
        assert ExportValidationService.validate_group_module(
            'parameters', field_label='Grupo'
        ) == 'parameters'
        with pytest.raises(ExportValidationException):
            ExportValidationService.validate_group_module('a b', field_label='Grupo')

    def test_filename_rules(self):
        assert ExportValidationService.validate_filename('export_x_2026.csv') == 'export_x_2026.csv'
        with pytest.raises(ExportValidationException):
            ExportValidationService.validate_filename('../escape.csv')
        with pytest.raises(ExportValidationException):
            ExportValidationService.validate_filename('dir/arquivo.csv')
        with pytest.raises(ExportValidationException):
            ExportValidationService.validate_filename('sem_extensao')

    def test_extension_match(self):
        ExportValidationService.validate_extension('x.csv', 'csv')
        with pytest.raises(ExportValidationException):
            ExportValidationService.validate_extension('x.xlsx', 'csv')


# ---------------------------------------------------------------------------
# Serviço de arquivos
# ---------------------------------------------------------------------------
class TestExportFileService:

    def test_build_filename(self):
        name = ExportFileService.build_filename('parameters.condominium_types', 'csv')
        assert name.startswith('export_parameters.condominium_types_')
        assert name.endswith('.csv')
        assert ':' not in name and ' ' not in name

    def test_build_filename_rejects_bad_service_key(self):
        with pytest.raises(ExportValidationException):
            ExportFileService.build_filename('../x', 'csv')

    def test_resolve_export_path_ok(self, export_root):
        (export_root / 'arquivo.csv').write_text('x')
        resolved = ExportFileService.resolve_export_path('arquivo.csv')
        assert resolved == export_root / 'arquivo.csv'

    def test_resolve_rejects_traversal(self, export_root):
        with pytest.raises(ExportValidationException):
            ExportFileService.resolve_export_path('../fora.csv')
        with pytest.raises(ExportValidationException):
            ExportFileService.resolve_export_path('sub/../../fora.csv')

    def test_resolve_rejects_absolute_path(self, export_root):
        with pytest.raises(ExportValidationException):
            ExportFileService.resolve_export_path('/etc/passwd')

    def test_resolve_rejects_url(self, export_root):
        with pytest.raises(ExportValidationException):
            ExportFileService.resolve_export_path('https://evil.example/x.csv')

    def test_resolve_rejects_symlink_outside(self, export_root, tmp_path):
        outside = tmp_path / 'fora.csv'
        outside.write_text('secreto')
        link = export_root / 'link.csv'
        link.symlink_to(outside)
        with pytest.raises(ExportValidationException):
            ExportFileService.resolve_export_path('link.csv')

    def test_remove_previous_file(self, export_root):
        (export_root / 'antigo.csv').write_text('dados')
        ExportFileService.remove_previous_file('antigo.csv')
        assert not (export_root / 'antigo.csv').exists()

    def test_remove_previous_file_empty_is_noop(self, export_root):
        ExportFileService.remove_previous_file('')

    def test_remove_previous_file_blocked_outside(self, export_root, tmp_path):
        outside = tmp_path / 'antigo.csv'
        outside.write_text('x')
        with pytest.raises(ExportValidationException):
            ExportFileService.remove_previous_file(str(outside))

    def test_remove_previous_file_missing_is_noop(self, export_root):
        # Registro aponta para arquivo que já não existe: re-exportar NÃO deve
        # falhar (arquivo removido manualmente ou volume recriado).
        ExportFileService.remove_previous_file('sumiu.csv')

    def test_validate_generated_file(self, export_root):
        (export_root / 'novo.csv').write_text('a;b\n1;2\n')
        resolved = ExportFileService.validate_generated_file(
            export_root / 'novo.csv', 'csv'
        )
        assert resolved.is_file()

    def test_validate_generated_file_empty(self, export_root):
        (export_root / 'vazio.csv').write_text('')
        with pytest.raises(ExportValidationException):
            ExportFileService.validate_generated_file(export_root / 'vazio.csv', 'csv')

    def test_validate_generated_file_wrong_extension(self, export_root):
        (export_root / 'novo.xlsx').write_text('x')
        with pytest.raises(ExportValidationException):
            ExportFileService.validate_generated_file(export_root / 'novo.xlsx', 'csv')

    def test_open_for_download(self, export_root):
        (export_root / 'ok.csv').write_text('a;b\n1;2\n')
        path, handle = ExportFileService.open_for_download('ok.csv')
        assert path.name == 'ok.csv'
        handle.close()

    def test_open_for_download_missing(self, export_root):
        with pytest.raises(ExportFileNotFound):
            ExportFileService.open_for_download('nao_existe.csv')

    def test_open_for_download_traversal(self, export_root):
        with pytest.raises(ExportFileNotFound):
            ExportFileService.open_for_download('../../etc/passwd')


# ---------------------------------------------------------------------------
# Orquestrador (ExportService)
# ---------------------------------------------------------------------------
class TestExportServiceEnqueue:

    def test_enqueue_sets_queued(self, _export):
        export = _export()
        ExportService.enqueue(export)
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.QUEUED

    def test_enqueue_rejects_inactive(self, _export):
        export = _export(is_active=False)
        with pytest.raises(ExportInvalidState):
            ExportService.enqueue(export)

    def test_enqueue_rejects_unknown_service(self, _export):
        export = _export(export_service='nao.registrado')
        with pytest.raises(ExportServiceNotFound):
            ExportService.enqueue(export)
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.PENDING

    def test_enqueue_rejects_processing(self, _export):
        export = _export(file_status=ExportModule.FileStatus.PROCESSING)
        with pytest.raises(ExportAlreadyProcessing):
            ExportService.enqueue(export)

    def test_enqueue_allows_completed_for_regeneration(self, _export, export_root):
        export = _export(file_status=ExportModule.FileStatus.COMPLETED)
        ExportService.enqueue(export)
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.QUEUED


class TestExportServiceRun:

    def test_run_generates_csv_and_completes(self, _export, export_root):
        # A fixture _condominium já cria um TypesCondominium; este é o segundo.
        TypesCondominium.objects.create(name='Residencial Teste')
        export = _export()
        result = ExportService.run(export.pk)
        assert result['status'] == 'completed'
        assert result['row_count'] == 2

        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.COMPLETED
        assert export.file_generate.endswith('.csv')
        assert export.generate_datetime is not None
        file = export_root / export.file_generate
        assert file.exists()
        assert 'Residencial Teste' in file.read_text(encoding='utf-8-sig')

    def test_run_generates_xlsx(self, _export, export_root):
        TypesCondominium.objects.create(name='Residencial XLSX')
        export = _export(file_format=ExportModule.FileFormat.XLSX)
        result = ExportService.run(export.pk)
        assert result['status'] == 'completed'
        export.refresh_from_db()
        assert export.file_generate.endswith('.xlsx')
        assert (export_root / export.file_generate).exists()

    def test_run_skips_when_processing(self, _export):
        export = _export(file_status=ExportModule.FileStatus.PROCESSING)
        result = ExportService.run(export.pk)
        assert result['status'] == 'skipped'
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.PROCESSING

    def test_run_unknown_service_marks_failed(self, _export, export_root):
        export = _export(export_service='nao.registrado')
        with pytest.raises(ExportServiceNotFound):
            ExportService.run(export.pk)
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.FAILED
        assert export.file_generate == ''

    def test_run_transient_error_marks_failed(self, _export, export_root, monkeypatch):
        export = _export()
        from domains.data_management.services.export_registry import registry as reg

        def boom(context):
            raise RuntimeError('falha transitória de filesystem')

        monkeypatch.setattr(reg.resolve('parameters.condominium_types'), 'generate', boom)
        with pytest.raises(RuntimeError):
            ExportService.run(export.pk)
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.FAILED

    def test_run_removes_previous_file(self, _export, export_root):
        TypesCondominium.objects.create(name='Novo')
        export = _export()
        ExportService.run(export.pk)
        export.refresh_from_db()

        # Simula um arquivo anterior órfão (nome gravado no registro).
        outdated = export_root / 'export_antigo.csv'
        outdated.write_text('dados antigos')
        export.file_generate = outdated.name
        export.save(update_fields=['file_generate'])

        # Nova geração remove o arquivo anterior antes de gerar.
        ExportService.run(export.pk)
        export.refresh_from_db()
        assert not outdated.exists()
        assert (export_root / export.file_generate).exists()
        assert export.file_generate != 'export_antigo.csv'

    def test_run_previous_file_missing_does_not_fail(self, _export, export_root):
        TypesCondominium.objects.create(name='Sem anterior')
        export = _export(
            file_status=ExportModule.FileStatus.COMPLETED,
            file_generate='sumiu.csv',
        )
        result = ExportService.run(export.pk)
        assert result['status'] == 'completed'
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.COMPLETED
        assert export.file_generate.endswith('.csv')

    def test_run_uses_export_service_registry_not_arbitrary_code(self, _export, export_root):
        export = _export(export_service='__import__.os.system')
        with pytest.raises(ExportServiceNotFound):
            ExportService.run(export.pk)
        export.refresh_from_db()
        assert export.file_status == ExportModule.FileStatus.FAILED


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------
class TestExportDownloadService:

    def test_download_completed_file(self, _export, export_root):
        TypesCondominium.objects.create(name='Download')
        export = _export()
        ExportService.run(export.pk)
        export.refresh_from_db()
        path, handle = ExportDownloadService.open_file(export)
        assert path.name == export.file_generate
        assert handle.read() != b''
        handle.close()

    def test_download_not_completed_rejected(self, _export):
        export = _export()
        with pytest.raises(ExportInvalidState):
            ExportDownloadService.open_file(export)

    def test_download_missing_file_rejected(self, _export, export_root):
        export = _export(
            file_status=ExportModule.FileStatus.COMPLETED,
            file_generate='nao_existe.csv',
        )
        with pytest.raises(ExportFileNotFound):
            ExportDownloadService.open_file(export)

    def test_download_malicious_path_rejected(self, _export, export_root):
        export = _export(
            file_status=ExportModule.FileStatus.COMPLETED,
            file_generate='../../etc/passwd',
        )
        with pytest.raises(ExportFileNotFound):
            ExportDownloadService.open_file(export)


# ---------------------------------------------------------------------------
# Exportadores (contrato ExportContext -> ExportResult)
# ---------------------------------------------------------------------------
class TestExporters:

    def test_condominium_types_exporter_generates_file(self, export_root):
        TypesCondominium.objects.create(name='Tipo 1', is_active=True)
        TypesCondominium.objects.create(name='Tipo 2', is_active=False)
        exporter = registry.resolve('parameters.condominium_types')
        dest = export_root / 'x.csv'
        context = ExportContext(
            export_id=1, condominium_id=None, file_format='csv', destination=dest
        )
        result = exporter.generate(context)
        assert result.row_count == 2
        text = dest.read_text(encoding='utf-8-sig')
        assert 'Tipo 1' in text and 'Tipo 2' in text
        assert 'Sim' in text and 'Não' in text  # bool virado em Sim/Não

    def test_collaborators_filter_by_condominium(self, _condominium, export_root):
        from domains.condominium.models import Collaborator

        Collaborator.objects.create(
            condominium=_condominium, name='Colab A', cpf='11111111111',
            rg='RG1', email='a@a.com', phone_number='11999999999',
        )
        exporter = registry.resolve('condominium.collaborators')
        dest = export_root / 'colab.csv'
        context = ExportContext(
            export_id=1, condominium_id=_condominium.pk,
            file_format='csv', destination=dest,
        )
        result = exporter.generate(context)
        assert result.row_count == 1
        text = dest.read_text(encoding='utf-8-sig')
        assert 'Colab A' in text

    def test_exporter_uses_streaming_iterator(self, _condominium, export_root, monkeypatch):
        exporter = registry.resolve('parameters.condominium_types')
        from django.db.models.query import QuerySet

        called = []

        def fake_iterator(self, *a, **k):
            called.append(True)
            return iter([])

        monkeypatch.setattr(QuerySet, 'iterator', fake_iterator)
        dest = export_root / 'x.csv'
        context = ExportContext(
            export_id=1, condominium_id=None, file_format='csv', destination=dest
        )
        exporter.generate(context)
        assert called, 'exportação deve iterar em streaming (iterator)'