from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from domains.reservations.models import Rentals
from domains.reservations.services.rentals_service import RentalsService


@pytest.mark.django_db
class TestRentalsModel:

    def test_defaults(self, unit, rental_type):
        rental = Rentals(
            condominium=unit,
            typesOfRentals=rental_type,
            startDate=date(2026, 1, 10),
            endDate=date(2026, 1, 15),
            applicant="Maria",
        )
        assert rental.status == Rentals.Status.AGENDAMENTO
        assert rental.is_active is True
        assert rental.charge_amount is True
        assert rental.errorStatus == ""
        assert rental.rentalPrice is None

    def test_str_contains_applicant(self, rental_factory):
        rental = rental_factory(applicant="João da Silva")
        assert "João da Silva" in str(rental)

    def test_end_date_before_start_date_is_rejected_by_database(
        self, unit, rental_type
    ):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Rentals.objects.create(
                    condominium=unit,
                    typesOfRentals=rental_type,
                    startDate=date(2026, 2, 10),
                    endDate=date(2026, 2, 1),
                    applicant="Inválido",
                    charge_amount=False,
                )

    def test_same_day_period_is_allowed(self, unit, rental_type):
        rental = Rentals.objects.create(
            condominium=unit,
            typesOfRentals=rental_type,
            startDate=date(2026, 3, 1),
            endDate=date(2026, 3, 1),
            applicant="Mesmo dia",
            charge_amount=False,
        )
        assert rental.pk is not None

    def test_status_is_not_editable(self):
        assert Rentals._meta.get_field("status").editable is False

    def test_audit_fields_are_not_editable(self):
        for field_name in ("created_by", "updated_by", "errorStatus"):
            assert Rentals._meta.get_field(field_name).editable is False

    def test_price_field_limits(self):
        field = Rentals._meta.get_field("rentalPrice")
        assert field.max_digits == 14
        assert field.decimal_places == 2
        assert field.null is True

    def test_service_initial_status_is_agendamento(
        self, unit, rental_type, admin_user
    ):
        rental = RentalsService.create_rental(
            {
                "condominium": unit,
                "typesOfRentals": rental_type,
                "startDate": date(2026, 4, 1),
                "endDate": date(2026, 4, 5),
                "applicant": "Novo",
                "rentalPrice": Decimal("50.00"),
                "charge_amount": True,
            },
            user=admin_user,
        )
        assert rental.status == Rentals.Status.AGENDAMENTO
