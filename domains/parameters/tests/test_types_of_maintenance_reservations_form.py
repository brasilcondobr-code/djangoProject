import pytest

from domains.parameters.forms import TypesOfMaintenanceReservationsForm
from domains.parameters.models.types_of_maintenance_reservations import (
    TypesOfMaintenanceReservations,
)


@pytest.mark.django_db
class TestTypesOfMaintenanceReservationsForm:

    def test_form_valid(self):
        form = TypesOfMaintenanceReservationsForm(
            data={'description': 'Manutenção Preventiva'}
        )
        assert form.is_valid(), form.errors

    def test_description_required(self):
        form = TypesOfMaintenanceReservationsForm(data={'description': ''})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_required_error_message(self):
        form = TypesOfMaintenanceReservationsForm(data={'description': ''})
        assert not form.is_valid()
        assert (
            'Informe a descrição do tipo de manutenção.'
            in str(form.errors['description'])
        )

    def test_description_only_spaces(self):
        form = TypesOfMaintenanceReservationsForm(data={'description': '   '})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_spaces_message(self):
        form = TypesOfMaintenanceReservationsForm(data={'description': '   '})
        assert not form.is_valid()
        assert (
            'Informe a descrição do tipo de manutenção.'
            in str(form.errors['description'])
        )

    def test_duplicate_description(self):
        TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Corretiva'
        )
        form = TypesOfMaintenanceReservationsForm(
            data={'description': 'Manutenção Corretiva'}
        )
        assert not form.is_valid()
        assert 'description' in form.errors
        assert (
            'Já existe um tipo de manutenção'
            in str(form.errors['description'])
        )

    def test_duplicate_description_case_insensitive(self):
        TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Preventiva'
        )
        form = TypesOfMaintenanceReservationsForm(
            data={'description': 'manutenção preventiva'}
        )
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_whitespace_normalized(self):
        form = TypesOfMaintenanceReservationsForm(
            data={'description': '  Manutenção Elétrica  '}
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data['description'] == 'Manutenção Elétrica'

    def test_own_description_on_edit(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Hidráulica'
        )
        form = TypesOfMaintenanceReservationsForm(
            instance=maintenance,
            data={'description': 'Manutenção Hidráulica  '},
        )
        assert form.is_valid(), form.errors

    def test_own_description_case_change_on_edit(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='Manutenção de Piscina'
        )
        form = TypesOfMaintenanceReservationsForm(
            instance=maintenance,
            data={'description': 'manutenção de piscina'},
        )
        assert form.is_valid(), form.errors

    def test_description_max_length(self):
        form = TypesOfMaintenanceReservationsForm(data={'description': 'x' * 256})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_is_active_default_initial(self):
        form = TypesOfMaintenanceReservationsForm()
        assert form.fields['is_active'].initial is True

    def test_is_active_not_required(self):
        form = TypesOfMaintenanceReservationsForm(
            data={'description': 'Manutenção Sazonal'}
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data['is_active'] in (False, True)

    def test_description_widget_attrs(self):
        form = TypesOfMaintenanceReservationsForm()
        attrs = form.fields['description'].widget.attrs
        assert attrs['class'] == 'form-control'
        assert attrs['placeholder'] == 'Informe a descrição do tipo de manutenção'
        assert attrs['maxlength'] == '255'

    def test_is_active_widget_attrs(self):
        form = TypesOfMaintenanceReservationsForm()
        assert form.fields['is_active'].widget.attrs['class'] == 'form-check-input'

    def test_labels(self):
        form = TypesOfMaintenanceReservationsForm()
        assert form.fields['description'].label == 'Descrição'
        assert form.fields['is_active'].label == 'Ativo'

    def test_description_help_text(self):
        form = TypesOfMaintenanceReservationsForm()
        assert 'descrição única' in form.fields['description'].help_text

    def test_is_active_help_text(self):
        form = TypesOfMaintenanceReservationsForm()
        assert 'utilizado em novos registros' in form.fields['is_active'].help_text

    def test_audit_fields_not_exposed(self):
        form = TypesOfMaintenanceReservationsForm()
        assert 'created_at' not in form.fields
        assert 'updated_at' not in form.fields
