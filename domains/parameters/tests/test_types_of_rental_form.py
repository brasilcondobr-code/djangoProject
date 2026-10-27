import pytest

from domains.parameters.forms import TypesOfRentalForm
from domains.parameters.models.types_of_rental import TypesOfRental


@pytest.mark.django_db
class TestTypesOfRentalForm:

    def test_form_valid(self):
        form = TypesOfRentalForm(data={'description': 'Locação Residencial'})
        assert form.is_valid(), form.errors

    def test_form_valid_with_numbers(self):
        form = TypesOfRentalForm(data={
            'description': 'Locação Residencial',
            'numberOfAppointments': '5',
            'numberOfReservations': '3',
        })
        assert form.is_valid(), form.errors
        assert form.cleaned_data['numberOfAppointments'] == 5
        assert form.cleaned_data['numberOfReservations'] == 3

    def test_number_of_appointments_optional(self):
        form = TypesOfRentalForm(data={'description': 'Locação Residencial'})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['numberOfAppointments'] is None

    def test_number_of_reservations_optional(self):
        form = TypesOfRentalForm(data={'description': 'Locação Residencial'})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['numberOfReservations'] is None

    def test_number_of_appointments_min_value_rejected(self):
        form = TypesOfRentalForm(data={
            'description': 'Locação Residencial',
            'numberOfAppointments': '0',
        })
        assert not form.is_valid()
        assert 'numberOfAppointments' in form.errors

    def test_number_of_reservations_min_value_rejected(self):
        form = TypesOfRentalForm(data={
            'description': 'Locação Residencial',
            'numberOfReservations': '0',
        })
        assert not form.is_valid()
        assert 'numberOfReservations' in form.errors

    def test_number_of_appointments_min_value_message(self):
        form = TypesOfRentalForm(data={
            'description': 'Locação Residencial',
            'numberOfAppointments': '0',
        })
        assert not form.is_valid()
        assert 'A quantidade de agendamentos deve ser no mínimo 1.' in str(form.errors['numberOfAppointments'])

    def test_number_of_reservations_min_value_message(self):
        form = TypesOfRentalForm(data={
            'description': 'Locação Residencial',
            'numberOfReservations': '0',
        })
        assert not form.is_valid()
        assert 'A quantidade de reservas deve ser no mínimo 1.' in str(form.errors['numberOfReservations'])

    def test_number_of_appointments_widget_attrs(self):
        form = TypesOfRentalForm()
        attrs = form.fields['numberOfAppointments'].widget.attrs
        assert attrs['class'] == 'form-control'
        assert attrs['placeholder'] == 'Informe a quantidade de agendamentos'

    def test_number_of_reservations_widget_attrs(self):
        form = TypesOfRentalForm()
        attrs = form.fields['numberOfReservations'].widget.attrs
        assert attrs['class'] == 'form-control'
        assert attrs['placeholder'] == 'Informe a quantidade de reservas'

    def test_number_of_appointments_help_text(self):
        form = TypesOfRentalForm()
        assert 'mínimo 1' in form.fields['numberOfAppointments'].help_text

    def test_number_of_reservations_help_text(self):
        form = TypesOfRentalForm()
        assert 'mínimo 1' in form.fields['numberOfReservations'].help_text

    def test_description_required(self):
        form = TypesOfRentalForm(data={'description': ''})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_spaces(self):
        form = TypesOfRentalForm(data={'description': '   '})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_spaces_message(self):
        form = TypesOfRentalForm(data={'description': '   '})
        assert not form.is_valid()
        assert 'Informe a descrição do tipo de locação.' in str(form.errors['description'])

    def test_required_error_message(self):
        form = TypesOfRentalForm(data={'description': ''})
        assert not form.is_valid()
        assert 'Informe a descrição do tipo de locação.' in str(form.errors['description'])

    def test_duplicate_description(self):
        TypesOfRental.objects.create(description='Locação Comercial')
        form = TypesOfRentalForm(data={'description': 'Locação Comercial'})
        assert not form.is_valid()
        assert 'description' in form.errors
        assert 'Já existe um tipo de locação' in str(form.errors['description'])

    def test_duplicate_description_case_insensitive(self):
        TypesOfRental.objects.create(description='Locação Residencial')
        form = TypesOfRentalForm(data={'description': 'locação residencial'})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_whitespace_normalized(self):
        form = TypesOfRentalForm(data={'description': '  Locação Temporada  '})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['description'] == 'Locação Temporada'

    def test_own_description_on_edit(self):
        rental = TypesOfRental.objects.create(description='Locação Anual')
        form = TypesOfRentalForm(
            instance=rental,
            data={'description': 'Locação Anual  '},
        )
        assert form.is_valid(), form.errors

    def test_own_description_case_change_on_edit(self):
        rental = TypesOfRental.objects.create(description='Locação Mensal')
        form = TypesOfRentalForm(
            instance=rental,
            data={'description': 'locação mensal'},
        )
        assert form.is_valid(), form.errors

    def test_description_max_length(self):
        form = TypesOfRentalForm(data={'description': 'x' * 256})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_is_active_default_initial(self):
        form = TypesOfRentalForm()
        assert form.fields['is_active'].initial is True

    def test_is_active_not_required(self):
        form = TypesOfRentalForm(data={'description': 'Locação Sazonal'})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['is_active'] in (False, True)

    def test_description_widget_attrs(self):
        form = TypesOfRentalForm()
        attrs = form.fields['description'].widget.attrs
        assert attrs['class'] == 'form-control'
        assert attrs['placeholder'] == 'Informe a descrição do tipo de locação'
        assert attrs['maxlength'] == '255'

    def test_is_active_widget_attrs(self):
        form = TypesOfRentalForm()
        assert form.fields['is_active'].widget.attrs['class'] == 'form-check-input'

    def test_description_help_text(self):
        form = TypesOfRentalForm()
        assert 'descrição única' in form.fields['description'].help_text

    def test_is_active_help_text(self):
        form = TypesOfRentalForm()
        assert 'utilizado em novos registros' in form.fields['is_active'].help_text

    def test_audit_fields_not_exposed(self):
        form = TypesOfRentalForm()
        assert 'created_at' not in form.fields
        assert 'updated_at' not in form.fields
