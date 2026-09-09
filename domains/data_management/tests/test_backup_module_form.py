import datetime

import pytest
from django import forms

from domains.data_management.forms import BackupModuleForm
from domains.data_management.models import BackupModule

pytestmark = pytest.mark.django_db


def _data(**overrides):
    data = {
        'title': 'Backup Mensal',
        'dateTime': '2026-09-07',
        'description': 'Backup de setembro',
        'is_active': True,
    }
    data.update(overrides)
    return data


class TestBackupModuleForm:

    def test_valid_form(self):
        form = BackupModuleForm(data=_data())
        assert form.is_valid(), form.errors
        backup = form.save()
        assert backup.pk is not None
        assert backup.status == BackupModule.Status.PENDING

    def test_title_required(self):
        form = BackupModuleForm(data=_data(title=''))
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_title_only_spaces_invalid(self):
        form = BackupModuleForm(data=_data(title='   '))
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_title_stripped_and_normalized(self):
        form = BackupModuleForm(data=_data(title='   Backup   Mensal  '))
        assert form.is_valid(), form.errors
        assert form.cleaned_data['title'] == 'Backup Mensal'

    def test_title_max_length(self):
        form = BackupModuleForm(data=_data(title='a' * 251))
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_date_required(self):
        form = BackupModuleForm(data=_data(dateTime=''))
        assert not form.is_valid()
        assert 'dateTime' in form.errors

    def test_invalid_date(self):
        form = BackupModuleForm(data=_data(dateTime='2026-13-40'))
        assert not form.is_valid()
        assert 'dateTime' in form.errors

    def test_impossible_date(self):
        form = BackupModuleForm(data=_data(dateTime='31/02/2026'))
        assert not form.is_valid()
        assert 'dateTime' in form.errors

    def test_description_optional(self):
        form = BackupModuleForm(data=_data(description=''))
        assert form.is_valid(), form.errors

    def test_is_active_default_checked(self):
        form = BackupModuleForm(data=_data())
        assert form.is_valid(), form.errors
        assert form.cleaned_data['is_active'] is True

    def test_duplicate_title_same_date_rejected(self):
        BackupModule.objects.create(
            title='Backup Mensal', dateTime=datetime.date(2026, 9, 7)
        )
        form = BackupModuleForm(data=_data())
        assert not form.is_valid()
        assert '__all__' in form.errors
        assert 'Já existe um backup' in str(form.errors['__all__'])

    def test_duplicate_title_different_date_allowed(self):
        BackupModule.objects.create(
            title='Backup Mensal', dateTime=datetime.date(2026, 9, 7)
        )
        form = BackupModuleForm(data=_data(dateTime='2026-10-01'))
        assert form.is_valid(), form.errors

    def test_duplicate_excludes_self_on_update(self):
        backup = BackupModule.objects.create(
            title='Backup Mensal', dateTime=datetime.date(2026, 9, 7)
        )
        form = BackupModuleForm(data=_data(), instance=backup)
        assert form.is_valid(), form.errors

    def test_technical_fields_not_editable(self):
        form = BackupModuleForm(data=_data())
        assert 'file_url' not in form.fields
        assert 'status' not in form.fields
        assert 'created_at' not in form.fields
        assert 'updated_at' not in form.fields

    def test_tampered_post_ignores_protected_fields(self):
        # POST adulterado tentando alterar file_url/status: o backend ignora.
        form = BackupModuleForm(
            data=_data(file_url='/etc/passwd', status='concluido')
        )
        assert form.is_valid(), form.errors
        assert 'file_url' not in form.cleaned_data
        assert 'status' not in form.cleaned_data
        backup = form.save()
        backup.refresh_from_db()
        assert backup.file_url == ''
        assert backup.status == BackupModule.Status.PENDING

    def test_widgets_and_placeholders(self):
        form = BackupModuleForm(data=_data())
        title_widget = form.fields['title'].widget
        assert isinstance(title_widget, forms.TextInput)
        assert title_widget.attrs['placeholder'] == 'Informe o título do backup'

        date_widget = form.fields['dateTime'].widget
        assert isinstance(date_widget, forms.DateInput)
        # DateInput consome o atributo 'type' como input_type (calendário HTML5).
        assert date_widget.input_type == 'date'
        assert date_widget.attrs['placeholder'] == 'Selecione a data do backup'

        desc_widget = form.fields['description'].widget
        assert isinstance(desc_widget, forms.Textarea)
        assert desc_widget.attrs['placeholder'] == 'Informe uma descrição opcional'

        active_widget = form.fields['is_active'].widget
        assert isinstance(active_widget, forms.CheckboxInput)

    def test_help_texts(self):
        form = BackupModuleForm(data=_data())
        assert form.fields['title'].help_text
        assert form.fields['dateTime'].help_text
        assert form.fields['is_active'].help_text

    def test_friendly_error_messages(self):
        form = BackupModuleForm(data=_data(title=''))
        assert 'O título é obrigatório.' in str(form.errors['title'])

        form = BackupModuleForm(data=_data(dateTime=''))
        assert 'A data do backup é obrigatória.' in str(form.errors['dateTime'])
