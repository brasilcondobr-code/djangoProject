import pytest
from django.forms import ValidationError
from domains.parameters.forms import AssemblyStatusForm
from domains.parameters.models.assembly_status import AssemblyStatus


@pytest.mark.django_db
class TestAssemblyStatusForm:

    def test_form_valid(self):
        form = AssemblyStatusForm(data={
            'description': 'Assembleia em andamento',
            'is_pending': False,
            'is_running': True,
            'is_complete': False,
        })
        assert form.is_valid(), form.errors

    def test_description_empty(self):
        form = AssemblyStatusForm(data={'description': ''})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_spaces(self):
        form = AssemblyStatusForm(data={'description': '   '})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_duplicate(self):
        AssemblyStatus.objects.create(description='Em execução')
        form = AssemblyStatusForm(data={'description': 'Em execução'})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_duplicate_case_insensitive(self):
        AssemblyStatus.objects.create(description='Em Execução')
        form = AssemblyStatusForm(data={'description': 'em execução'})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_whitespace_normalized(self):
        form = AssemblyStatusForm(data={'description': '  Em execução  '})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['description'] == 'Em execução'

    def test_error_messages(self):
        form = AssemblyStatusForm(data={'description': ''})
        assert not form.is_valid()
        assert 'obrigatória' in str(form.errors['description'])

        AssemblyStatus.objects.create(description='Pendente')
        form = AssemblyStatusForm(data={'description': 'Pendente'})
        assert not form.is_valid()
        assert 'já existe' in str(form.errors['description']).lower()

    def test_own_description_not_duplicate_on_edit(self):
        status = AssemblyStatus.objects.create(description='Pendente')
        form = AssemblyStatusForm(
            instance=status,
            data={'description': 'Pendente  '},
        )
        assert form.is_valid(), form.errors

    def test_widgets(self):
        form = AssemblyStatusForm()
        assert form.fields['description'].widget.attrs.get('placeholder') is not None
        assert form.fields['description'].widget.attrs.get('maxlength') == '255'

    def test_help_texts(self):
        form = AssemblyStatusForm()
        assert 'Informe uma descrição única' in form.fields['description'].help_text
        assert 'execução' in form.fields['is_running'].help_text
        assert 'concluída' in form.fields['is_complete'].help_text

    def test_is_pending_default(self):
        form = AssemblyStatusForm()
        assert form.fields['is_pending'].initial is True

    def test_is_active_default(self):
        form = AssemblyStatusForm()
        assert form.fields['is_active'].initial is True