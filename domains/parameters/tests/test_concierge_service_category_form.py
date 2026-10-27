import pytest

from domains.parameters.forms import ConciergeServiceCategoryForm
from domains.parameters.models.concierge_service_categories import ConciergeServiceCategory


@pytest.mark.django_db
class TestConciergeServiceCategoryForm:

    def test_form_valid(self):
        form = ConciergeServiceCategoryForm(data={'description': 'Entrega de encomendas'})
        assert form.is_valid(), form.errors

    def test_description_required(self):
        form = ConciergeServiceCategoryForm(data={'description': ''})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_spaces(self):
        form = ConciergeServiceCategoryForm(data={'description': '   '})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_spaces_message(self):
        form = ConciergeServiceCategoryForm(data={'description': '   '})
        assert not form.is_valid()
        assert 'Informe a descrição da categoria de serviço portaria.' in str(form.errors['description'])

    def test_required_error_message(self):
        form = ConciergeServiceCategoryForm(data={'description': ''})
        assert not form.is_valid()
        assert 'Informe a descrição da categoria de serviço portaria.' in str(form.errors['description'])

    def test_duplicate_description(self):
        ConciergeServiceCategory.objects.create(description='Portaria 24 horas')
        form = ConciergeServiceCategoryForm(data={'description': 'Portaria 24 horas'})
        assert not form.is_valid()
        assert 'description' in form.errors
        assert 'Já existe uma categoria de serviço portaria' in str(form.errors['description'])

    def test_duplicate_description_case_insensitive(self):
        ConciergeServiceCategory.objects.create(description='Recebimento de Correspondências')
        form = ConciergeServiceCategoryForm(data={'description': 'recebimento de correspondências'})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_whitespace_normalized(self):
        form = ConciergeServiceCategoryForm(data={'description': '  Chaveiro Eletrônico  '})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['description'] == 'Chaveiro Eletrônico'

    def test_own_description_on_edit(self):
        category = ConciergeServiceCategory.objects.create(description='Segurança')
        form = ConciergeServiceCategoryForm(
            instance=category,
            data={'description': 'Segurança  '},
        )
        assert form.is_valid(), form.errors

    def test_own_description_case_change_on_edit(self):
        category = ConciergeServiceCategory.objects.create(description='Portaria')
        form = ConciergeServiceCategoryForm(
            instance=category,
            data={'description': 'portaria'},
        )
        assert form.is_valid(), form.errors

    def test_description_max_length(self):
        form = ConciergeServiceCategoryForm(data={'description': 'x' * 256})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_is_active_default_initial(self):
        form = ConciergeServiceCategoryForm()
        assert form.fields['is_active'].initial is True

    def test_is_active_not_required(self):
        form = ConciergeServiceCategoryForm(data={'description': 'Elevador'})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['is_active'] in (False, True)

    def test_description_widget_attrs(self):
        form = ConciergeServiceCategoryForm()
        attrs = form.fields['description'].widget.attrs
        assert attrs['class'] == 'form-control'
        assert attrs['placeholder'] == 'Informe a descrição da categoria de serviço portaria'
        assert attrs['maxlength'] == '255'

    def test_is_active_widget_attrs(self):
        form = ConciergeServiceCategoryForm()
        assert form.fields['is_active'].widget.attrs['class'] == 'form-check-input'

    def test_description_help_text(self):
        form = ConciergeServiceCategoryForm()
        assert 'descrição única' in form.fields['description'].help_text

    def test_is_active_help_text(self):
        form = ConciergeServiceCategoryForm()
        assert 'utilizada em novos registros' in form.fields['is_active'].help_text

    def test_audit_fields_not_exposed(self):
        form = ConciergeServiceCategoryForm()
        assert 'created_at' not in form.fields
        assert 'updated_at' not in form.fields
