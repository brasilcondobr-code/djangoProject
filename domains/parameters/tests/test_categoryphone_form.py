import pytest

from domains.parameters.forms import CategoryPhoneForm
from domains.parameters.models.categoryphone import CategoryPhone


@pytest.mark.django_db
class TestCategoryPhoneForm:

    def test_form_valid(self):
        form = CategoryPhoneForm(data={'name': 'Academia', 'is_active': True})
        assert form.is_valid(), form.errors

    def test_name_required(self):
        form = CategoryPhoneForm(data={'name': ''})
        assert not form.is_valid()
        assert 'name' in form.errors
        assert 'Informe o nome da categoria de telefone.' in str(form.errors['name'])

    def test_name_only_spaces(self):
        form = CategoryPhoneForm(data={'name': '   '})
        assert not form.is_valid()
        assert 'name' in form.errors
        assert 'Informe o nome da categoria de telefone.' in str(form.errors['name'])

    def test_name_is_stripped(self):
        form = CategoryPhoneForm(data={'name': '  Academia  ', 'is_active': True})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['name'] == 'Academia'

    def test_duplicate_name_rejected(self):
        CategoryPhone.objects.create(name='Academia')
        form = CategoryPhoneForm(data={'name': 'Academia'})
        assert not form.is_valid()
        assert 'Já existe uma categoria de telefone' in str(form.errors['name'])

    def test_duplicate_name_case_insensitive(self):
        CategoryPhone.objects.create(name='Academia')
        form = CategoryPhoneForm(data={'name': 'ACADEMIA'})
        assert not form.is_valid()

    def test_duplicate_excludes_own_instance(self):
        category = CategoryPhone.objects.create(name='Academia')
        form = CategoryPhoneForm(data={'name': 'Academia'}, instance=category)
        assert form.is_valid(), form.errors

    def test_widgets_and_labels(self):
        form = CategoryPhoneForm()
        name_widget = form.fields['name'].widget
        assert name_widget.attrs['class'] == 'form-control'
        assert 'categoria de telefone' in name_widget.attrs['placeholder']
        assert form.fields['name'].label == 'Nome'
        assert form.fields['is_active'].label == 'Ativo'
        assert 'não pode conter apenas espaços' not in form.fields['name'].help_text
        assert 'nome único' in form.fields['name'].help_text
