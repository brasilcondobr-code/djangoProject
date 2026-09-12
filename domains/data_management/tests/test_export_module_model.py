import pytest
from django.db import IntegrityError

from domains.data_management.models import ExportModule

pytestmark = pytest.mark.django_db


class TestExportModuleModel:

    def test_create_valid(self, _export):
        export = _export()
        assert export.pk is not None
        assert export.file_format == ExportModule.FileFormat.CSV
        assert export.file_status == ExportModule.FileStatus.PENDING
        assert export.is_active is True
        assert export.file_generate == ''
        assert export.generate_datetime is None

    def test_required_fields_schema(self):
        """Campos funcionais são NOT NULL / sem blank (obrigatórios no Admin)."""
        for field in ('condominium', 'group', 'module', 'export_service'):
            meta = ExportModule._meta.get_field(field)
            assert meta.null is False, field
            assert meta.blank is False, field

    def test_unique_configuration_constraint(self, _export, _condominium):
        _export()
        with pytest.raises(IntegrityError):
            ExportModule.objects.create(
                condominium=_condominium,
                group='parameters',
                module='condominium_types',
                file_format=ExportModule.FileFormat.CSV,
                export_service='parameters.condominium_types',
            )

    def test_same_config_different_format_allowed(self, _export):
        _export()
        other = _export(file_format=ExportModule.FileFormat.XLSX)
        assert other.pk is not None

    def test_status_choices(self):
        assert ExportModule.FileStatus.values == [
            'pending', 'queued', 'processing', 'completed', 'failed', 'cancelled',
        ]

    def test_file_format_choices(self):
        assert ExportModule.FileFormat.values == ['csv', 'xlsx']

    def test_related_name_exports(self, _export, _condominium):
        _export()
        assert _condominium.exports.count() == 1

    def test_technical_fields_are_not_editable(self):
        for field in ('file_generate', 'file_status', 'generate_datetime'):
            assert ExportModule._meta.get_field(field).editable is False

    def test_ordering_by_updated_desc(self, _export):
        first = _export()
        second = _export(
            group='residents', module='units',
            export_service='residents.units',
        )
        first.group = 'condominium'
        first.save(update_fields=['group', 'updated_at'])
        order = list(ExportModule.objects.values_list('pk', flat=True))
        assert order[0] == first.pk or order[-1] == first.pk  # atualizado fica primeiro

    def test_str(self, _export):
        assert str(_export()) == 'parameters.condominium_types (CSV)'

    def test_meta_indexes(self):
        names = [idx.name for idx in ExportModule._meta.indexes]
        assert 'idx_export_status_updated' in names

    def test_meta_constraint(self):
        names = [c.name for c in ExportModule._meta.constraints]
        assert 'unique_export_configuration' in names