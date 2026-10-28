from datetime import date
from decimal import Decimal

import pytest

from domains.parameters.models import TypesOfRental
from domains.reservations.forms import RentalsForm
from domains.reservations.models import Rentals


def form_data(unit, rental_type, **overrides):
    data = {
        "condominium": unit.pk,
        "typesOfRentals": rental_type.pk,
        "startDate": "2026-05-10",
        "endDate": "2026-05-15",
        "applicant": "  Maria Souza  ",
        "rentalPrice": "150,00",
        "charge_amount": True,
        "observations": "  Teste  ",
        "is_active": True,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestRentalsForm:

    def test_valid_form(self, unit, rental_type):
        form = RentalsForm(data=form_data(unit, rental_type))
        assert form.is_valid(), form.errors
        assert form.cleaned_data["applicant"] == "Maria Souza"
        assert form.cleaned_data["rentalPrice"] == Decimal("150.00")

    def test_price_with_thousand_separator(self, unit, rental_type):
        form = RentalsForm(
            data=form_data(unit, rental_type, rentalPrice="1.234,56")
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["rentalPrice"] == Decimal("1234.56")

    def test_price_with_too_many_digits_is_rejected(
        self, unit, rental_type
    ):
        form = RentalsForm(
            data=form_data(
                unit, rental_type, rentalPrice="1234567890123,00"
            )
        )
        assert not form.is_valid()
        assert "14" in str(form.errors["rentalPrice"])

    def test_status_is_not_part_of_the_form(self, unit, rental_type):
        form = RentalsForm(data=form_data(unit, rental_type))
        assert "status" not in form.fields
        assert "created_by" not in form.fields
        assert "updated_by" not in form.fields

    @pytest.mark.parametrize(
        "field",
        ["condominium", "typesOfRentals", "startDate", "endDate", "applicant"],
    )
    def test_required_fields(self, unit, rental_type, field):
        data = form_data(unit, rental_type)
        data.pop(field)
        form = RentalsForm(data=data)
        assert not form.is_valid()
        assert field in form.errors

    def test_end_date_before_start_date(self, unit, rental_type):
        form = RentalsForm(
            data=form_data(
                unit,
                rental_type,
                startDate="2026-05-15",
                endDate="2026-05-10",
            )
        )
        assert not form.is_valid()
        assert "endDate" in form.errors
        assert "maior ou igual" in str(form.errors["endDate"])

    def test_charge_enabled_requires_price(self, unit, rental_type):
        form = RentalsForm(
            data=form_data(unit, rental_type, rentalPrice="")
        )
        assert not form.is_valid()
        assert "rentalPrice" in form.errors

    def test_charge_enabled_requires_positive_price(self, unit, rental_type):
        form = RentalsForm(
            data=form_data(unit, rental_type, rentalPrice="0,00")
        )
        assert not form.is_valid()
        assert "maior que zero" in str(form.errors["rentalPrice"])

    def test_charge_disabled_clears_price(self, unit, rental_type):
        form = RentalsForm(
            data=form_data(
                unit,
                rental_type,
                charge_amount=False,
                rentalPrice="200,00",
            )
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["rentalPrice"] is None

    def test_charge_disabled_accepts_empty_price(self, unit, rental_type):
        form = RentalsForm(
            data=form_data(
                unit,
                rental_type,
                charge_amount=False,
                rentalPrice="",
            )
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["rentalPrice"] is None

    def test_edit_charge_disabled_without_price_field_clears_price(
        self, unit, rental_type, rental_factory
    ):
        rental = rental_factory(rentalPrice=Decimal("100.00"))
        data = form_data(unit, rental_type, charge_amount=False)
        data.pop("rentalPrice")

        form = RentalsForm(data=data, instance=rental)

        assert form.is_valid(), form.errors
        assert form.cleaned_data["rentalPrice"] is None
        assert form.save().rentalPrice is None

    def test_charge_enabled_without_price_field_is_rejected(
        self, unit, rental_type
    ):
        data = form_data(unit, rental_type)
        data.pop("rentalPrice")

        form = RentalsForm(data=data)

        assert not form.is_valid()
        assert "Informe o valor da locação" in str(form.errors["rentalPrice"])

    def test_blank_applicant_is_rejected(self, unit, rental_type):
        form = RentalsForm(
            data=form_data(unit, rental_type, applicant="   ")
        )
        assert not form.is_valid()
        assert "applicant" in form.errors

    def test_inactive_type_is_not_offered(self, unit, rental_type):
        rental_type.is_active = False
        rental_type.save(update_fields=["is_active"])
        form = RentalsForm()
        assert rental_type not in form.fields["typesOfRentals"].queryset

    def test_selected_inactive_type_is_preserved_on_edit(
        self, unit, rental_type
    ):
        rental = Rentals.objects.create(
            condominium=unit,
            typesOfRentals=rental_type,
            startDate=date(2026, 6, 1),
            endDate=date(2026, 6, 2),
            applicant="Teste",
            charge_amount=False,
        )
        rental_type.is_active = False
        rental_type.save(update_fields=["is_active"])
        form = RentalsForm(instance=rental)
        assert rental_type in form.fields["typesOfRentals"].queryset

    def test_capacity_limit_reached_rejects_form(self, unit, rental_type):
        rental_type.numberOfAppointments = 2
        rental_type.save(update_fields=["numberOfAppointments"])
        for day in (10, 12):
            Rentals.objects.create(
                condominium=unit,
                typesOfRentals=rental_type,
                startDate=date(2026, 5, day),
                endDate=date(2026, 5, day + 1),
                applicant="Existente",
                charge_amount=False,
            )
        form = RentalsForm(data=form_data(unit, rental_type))
        assert not form.is_valid()
        assert "Limite de 2 agendamentos" in str(form.non_field_errors())

    def test_null_limit_rejects_form(self, unit, rental_type):
        rental_type.numberOfAppointments = None
        rental_type.save(update_fields=["numberOfAppointments"])
        form = RentalsForm(data=form_data(unit, rental_type))
        assert not form.is_valid()
        assert "não possui limite" in str(form.non_field_errors())

    def test_edit_excludes_own_record_from_capacity(self, unit, rental_type):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        rental = Rentals.objects.create(
            condominium=unit,
            typesOfRentals=rental_type,
            startDate=date(2026, 7, 1),
            endDate=date(2026, 7, 5),
            applicant="Original",
            charge_amount=False,
        )
        form = RentalsForm(
            data=form_data(
                unit,
                rental_type,
                startDate="2026-07-02",
                endDate="2026-07-04",
                charge_amount=False,
                rentalPrice="",
            ),
            instance=rental,
        )
        assert form.is_valid(), form.errors

    def test_edit_of_reserved_rental_is_rejected(self, unit, rental_type):
        rental = Rentals.objects.create(
            condominium=unit,
            typesOfRentals=rental_type,
            startDate=date(2026, 8, 1),
            endDate=date(2026, 8, 2),
            applicant="Reservada",
            charge_amount=False,
            status=Rentals.Status.RESERVADO,
        )
        form = RentalsForm(
            data=form_data(
                unit,
                rental_type,
                startDate="2026-08-01",
                endDate="2026-08-03",
                charge_amount=False,
                rentalPrice="",
            ),
            instance=rental,
        )
        assert not form.is_valid()
        assert "Somente locações em Agendamento" in str(
            form.non_field_errors()
        )

    def test_capacity_isolated_by_unit(self, unit, other_unit, rental_type):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        Rentals.objects.create(
            condominium=other_unit,
            typesOfRentals=rental_type,
            startDate=date(2026, 9, 1),
            endDate=date(2026, 9, 5),
            applicant="Outra unidade",
            charge_amount=False,
        )
        form = RentalsForm(data=form_data(unit, rental_type))
        assert form.is_valid(), form.errors

    def test_capacity_isolated_by_type(
        self, unit, rental_type, other_rental_type
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        Rentals.objects.create(
            condominium=unit,
            typesOfRentals=other_rental_type,
            startDate=date(2026, 9, 1),
            endDate=date(2026, 9, 5),
            applicant="Outro tipo",
            charge_amount=False,
        )
        form = RentalsForm(data=form_data(unit, rental_type))
        assert form.is_valid(), form.errors

    def test_model_validation_keeps_inactive_option(self, unit):
        inactive = TypesOfRental.objects.create(
            description="Inativo", is_active=False
        )
        form = RentalsForm()
        assert inactive not in form.fields["typesOfRentals"].queryset
