import pytest
from django.db import IntegrityError

from domains.parameters.models.types_of_rental import TypesOfRental


@pytest.mark.django_db
class TestTypesOfRentalModel:

    def test_create_valid(self):
        rental = TypesOfRental.objects.create(description='Locação Residencial')
        assert rental.pk is not None
        assert rental.description == 'Locação Residencial'

    def test_default_is_active_true(self):
        rental = TypesOfRental.objects.create(description='Locação Comercial')
        assert rental.is_active is True

    def test_number_of_appointments_default_none(self):
        rental = TypesOfRental.objects.create(description='Locação Comercial')
        assert rental.numberOfAppointments is None

    def test_number_of_reservations_default_none(self):
        rental = TypesOfRental.objects.create(description='Locação Comercial')
        assert rental.numberOfReservations is None

    def test_number_of_appointments_min_value_validator(self):
        field = TypesOfRental._meta.get_field('numberOfAppointments')
        assert field.validators[0].limit_value == 1

    def test_number_of_reservations_min_value_validator(self):
        field = TypesOfRental._meta.get_field('numberOfReservations')
        assert field.validators[0].limit_value == 1

    def test_number_of_appointments_null_blank_true(self):
        field = TypesOfRental._meta.get_field('numberOfAppointments')
        assert field.null is True
        assert field.blank is True

    def test_number_of_reservations_null_blank_true(self):
        field = TypesOfRental._meta.get_field('numberOfReservations')
        assert field.null is True
        assert field.blank is True

    def test_create_with_numbers(self):
        rental = TypesOfRental.objects.create(
            description='Locação com Limites',
            numberOfAppointments=5,
            numberOfReservations=3,
        )
        assert rental.numberOfAppointments == 5
        assert rental.numberOfReservations == 3

    def test_created_at_auto_set(self):
        rental = TypesOfRental.objects.create(description='Locação Temporada')
        assert rental.created_at is not None

    def test_updated_at_changes_on_update(self):
        rental = TypesOfRental.objects.create(description='Locação Anual')
        original_updated = rental.updated_at
        rental.description = 'Locação Anual Renovada'
        rental.save()
        rental.refresh_from_db()
        assert rental.updated_at >= original_updated

    def test_str_returns_description(self):
        rental = TypesOfRental.objects.create(description='Locação Mensal')
        assert str(rental) == 'Locação Mensal'

    def test_duplicate_description_raises(self):
        TypesOfRental.objects.create(description='Locação Diária')
        with pytest.raises(IntegrityError):
            TypesOfRental.objects.create(description='Locação Diária')

    def test_description_required(self):
        with pytest.raises(IntegrityError):
            TypesOfRental.objects.create(description=None)

    def test_description_max_length(self):
        field = TypesOfRental._meta.get_field('description')
        assert field.max_length == 255

    def test_description_unique_flag(self):
        field = TypesOfRental._meta.get_field('description')
        assert field.unique is True

    def test_verbose_names(self):
        assert TypesOfRental._meta.verbose_name == '27. Tipo de Locação'
        assert TypesOfRental._meta.verbose_name_plural == '27. Tipos de Locações'

    def test_db_table(self):
        assert TypesOfRental._meta.db_table == 'parameters_typesofrentals'

    def test_ordering(self):
        assert TypesOfRental._meta.ordering == ['description']

    def test_created_after_updated(self):
        first = TypesOfRental.objects.create(description='Aaa')
        second = TypesOfRental.objects.create(description='Bbb')
        assert list(TypesOfRental.objects.all()) == [first, second]
