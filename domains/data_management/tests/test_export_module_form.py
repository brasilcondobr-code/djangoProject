import pytest
from django import forms as django_forms

from domains.data_management.forms import ExportModuleForm
from domains.data_management.models import ExportModule

pytestmark = pytest.mark.django_db


class TestExportModuleForm:

    def _data(self, **overrides):
        data = dict(
            condominium=1,
            group='parameters',
            module='condominium_types',
            file_format=ExportModule.FileFormat.CSV,
            export_service='parameters.condominium_types',
            description='Exportação de teste',
            is_active='on',
        )
        data.update(overrides)
        return data

    def test_valid_form(self, _condominium):
        form = ExportModuleForm(data=self._data(condominium=_condominium.pk))
        assert form.is_valid(), form.errors

    def test_technical_fields_not_in_form(self, _export):
        """Submissões manipuladas de campos técnicos são ignoradas pelo Django."""
        export = _export()
        form = ExportModuleForm(instance=export)
        for field in (
            'file_generate', 'file_status', 'generate_datetime',
            'created_at', 'updated_at',
        ):
            assert field not in form.fields

    def test_widgets_classes_and_placeholders(self):
        form = ExportModuleForm()
        assert form.fields['group'].widget.attrs['class'] == 'form-control'
        assert form.fields['group'].widget.attrs['placeholder'] == 'parameters'
        assert form.fields['module'].widget.attrs['placeholder'] == 'condominium_types'
        assert (
            form.fields['export_service'].widget.attrs['placeholder']
            == 'parameters.condominium_types'
        )
        assert isinstance(form.fields['file_format'].widget, django_forms.Select)
        assert isinstance(form.fields['description'].widget, django_forms.Textarea)
        assert isinstance(form.fields['is_active'].widget, django_forms.CheckboxInput)

    def test_help_texts(self):
        form = ExportModuleForm()
        assert 'ex.: parameters' in form.fields['group'].help_text.lower()
        assert 'chave do serviço' in form.fields['export_service'].help_text.lower()
        assert 'csv ou xlsx' in form.fields['file_format'].help_text.lower()

    def test_rejects_forbidden_chars_in_group(self, _condominium):
        form = ExportModuleForm(
            data=self._data(condominium=_condominium.pk, group='parametros; DROP')
        )
        assert not form.is_valid()
        assert 'caracteres não permitidos' in form.errors['group'][0]

    def test_rejects_forbidden_chars_in_export_service(self, _condominium):
        form = ExportModuleForm(
            data=self._data(condominium=_condominium.pk, export_service='a/b/c')
        )
        assert not form.is_valid()
        assert 'caracteres não permitidos' in form.errors['export_service'][0]

    def test_rejects_duplicate_configuration(self, _export, _condominium):
        _export()
        form = ExportModuleForm(
            data=self._data(condominium=_condominium.pk)
        )
        assert not form.is_valid()
        assert 'Já existe uma configuração' in str(form.errors)

    def test_rejects_duplicate_excluding_self(self, _export, _condominium):
        export = _export()
        form = ExportModuleForm(
            data=self._data(condominium=_condominium.pk),
            instance=export,
        )
        assert form.is_valid(), form.errors

    def test_required_messages(self):
        form = ExportModuleForm(data={})
        assert not form.is_valid()
        assert 'O condomínio é obrigatório.' in form.errors['condominium']
        assert 'O grupo é obrigatório.' in form.errors['group']
        assert 'O módulo é obrigatório.' in form.errors['module']
        assert 'O serviço de exportação é obrigatório.' in form.errors['export_service']