from datetime import date
from decimal import Decimal

import pytest

from domains.reservations.exceptions import (
    RentalCapacityError,
    RentalTransitionError,
    RentalValidationError,
)
from domains.reservations.models import Rentals
from domains.reservations.services.rentals_service import RentalsService


def rental_data(unit, rental_type, **overrides):
    data = {
        "condominium": unit,
        "typesOfRentals": rental_type,
        "startDate": date(2026, 1, 10),
        "endDate": date(2026, 1, 15),
        "applicant": "  Maria Souza  ",
        "rentalPrice": Decimal("100.00"),
        "charge_amount": True,
        "observations": "  Observação  ",
        "is_active": True,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestRentalCreate:

    def test_create_sets_initial_status_and_audit(
        self, unit, rental_type, admin_user
    ):
        rental = RentalsService.create_rental(
            rental_data(unit, rental_type), user=admin_user
        )

        assert rental.pk is not None
        assert rental.status == Rentals.Status.AGENDAMENTO
        assert rental.created_by == admin_user
        assert rental.updated_by == admin_user
        assert rental.errorStatus == ""
        assert rental.applicant == "Maria Souza"
        assert rental.observations == "Observação"

    def test_create_ignores_client_status_and_audit(
        self, unit, rental_type, admin_user, other_user
    ):
        data = rental_data(unit, rental_type)
        data.update(
            {
                "status": Rentals.Status.FINALIZADO,
                "created_by": other_user,
                "updated_by": other_user,
                "errorStatus": "erro forjado",
            }
        )

        rental = RentalsService.create_rental(data, user=admin_user)

        assert rental.status == Rentals.Status.AGENDAMENTO
        assert rental.created_by == admin_user
        assert rental.updated_by == admin_user
        assert rental.errorStatus == ""

    def test_create_without_user_leaves_audit_empty(self, unit, rental_type):
        rental = RentalsService.create_rental(rental_data(unit, rental_type))
        assert rental.created_by is None
        assert rental.updated_by is None

    def test_create_normalizes_string_booleans(
        self, unit, rental_type, admin_user
    ):
        rental = RentalsService.create_rental(
            rental_data(
                unit,
                rental_type,
                charge_amount="False",
                rentalPrice=Decimal("10.00"),
                is_active="false",
            ),
            user=admin_user,
        )
        assert rental.charge_amount is False
        assert rental.rentalPrice is None
        assert rental.is_active is False

    def test_charge_disabled_clears_price(self, unit, rental_type, admin_user):
        rental = RentalsService.create_rental(
            rental_data(
                unit,
                rental_type,
                charge_amount=False,
                rentalPrice=Decimal("99.99"),
            ),
            user=admin_user,
        )
        assert rental.rentalPrice is None

    @pytest.mark.parametrize(
        "field,value",
        [
            ("startDate", None),
            ("endDate", None),
            ("applicant", "   "),
        ],
    )
    def test_required_fields_are_validated(
        self, unit, rental_type, admin_user, field, value
    ):
        data = rental_data(unit, rental_type)
        data[field] = value
        with pytest.raises(RentalValidationError):
            RentalsService.create_rental(data, user=admin_user)
        assert Rentals.objects.count() == 0

    def test_end_date_before_start_date_is_rejected(
        self, unit, rental_type, admin_user
    ):
        with pytest.raises(RentalValidationError) as exc:
            RentalsService.create_rental(
                rental_data(
                    unit,
                    rental_type,
                    startDate=date(2026, 2, 10),
                    endDate=date(2026, 2, 1),
                ),
                user=admin_user,
            )
        assert "maior ou igual" in str(exc.value)

    def test_same_day_period_is_accepted(
        self, unit, rental_type, admin_user
    ):
        rental = RentalsService.create_rental(
            rental_data(
                unit,
                rental_type,
                startDate=date(2026, 2, 1),
                endDate=date(2026, 2, 1),
            ),
            user=admin_user,
        )
        assert rental.pk is not None

    @pytest.mark.parametrize("price", [None, Decimal("0.00"), ""])
    def test_charge_enabled_requires_positive_price(
        self, unit, rental_type, admin_user, price
    ):
        with pytest.raises(RentalValidationError):
            RentalsService.create_rental(
                rental_data(unit, rental_type, rentalPrice=price),
                user=admin_user,
            )


@pytest.mark.django_db
class TestRentalCapacity:

    def _existing(self, unit, rental_type, **overrides):
        data = rental_data(unit, rental_type, charge_amount=False,
                           rentalPrice=None)
        data.update(overrides)
        return Rentals.objects.create(**data)

    def test_overlap_on_boundary_is_counted(
        self, unit, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        self._existing(
            unit,
            rental_type,
            startDate=date(2026, 1, 10),
            endDate=date(2026, 1, 15),
        )

        with pytest.raises(RentalCapacityError):
            RentalsService.create_rental(
                rental_data(
                    unit,
                    rental_type,
                    startDate=date(2026, 1, 15),
                    endDate=date(2026, 1, 20),
                ),
                user=admin_user,
            )

    def test_non_overlapping_period_is_accepted(
        self, unit, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        self._existing(
            unit,
            rental_type,
            startDate=date(2026, 1, 10),
            endDate=date(2026, 1, 15),
        )

        rental = RentalsService.create_rental(
            rental_data(
                unit,
                rental_type,
                startDate=date(2026, 1, 16),
                endDate=date(2026, 1, 20),
            ),
            user=admin_user,
        )
        assert rental.pk is not None

    def test_capacity_is_isolated_by_unit(
        self, unit, other_unit, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        self._existing(unit, rental_type)

        rental = RentalsService.create_rental(
            rental_data(other_unit, rental_type),
            user=admin_user,
        )
        assert rental.pk is not None

    def test_capacity_is_isolated_by_rental_type(
        self, unit, rental_type, other_rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        self._existing(unit, rental_type)

        rental = RentalsService.create_rental(
            rental_data(unit, other_rental_type),
            user=admin_user,
        )
        assert rental.pk is not None

    def test_inactive_records_are_not_counted(
        self, unit, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        self._existing(unit, rental_type, is_active=False)

        rental = RentalsService.create_rental(
            rental_data(unit, rental_type), user=admin_user
        )
        assert rental.pk is not None

    def test_records_in_other_status_are_not_counted(
        self, unit, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        self._existing(
            unit,
            rental_type,
            status=Rentals.Status.RESERVADO,
        )

        rental = RentalsService.create_rental(
            rental_data(unit, rental_type), user=admin_user
        )
        assert rental.pk is not None

    def test_up_to_limit_is_accepted_and_limit_plus_one_is_rejected(
        self, unit, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 2
        rental_type.save(update_fields=["numberOfAppointments"])

        for _ in range(2):
            RentalsService.create_rental(
                rental_data(unit, rental_type), user=admin_user
            )

        assert Rentals.objects.filter(
            status=Rentals.Status.AGENDAMENTO
        ).count() == 2

        with pytest.raises(RentalCapacityError):
            RentalsService.create_rental(
                rental_data(unit, rental_type), user=admin_user
            )

    def test_zero_limit_blocks_creation(
        self, unit, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 0
        rental_type.save(update_fields=["numberOfAppointments"])

        with pytest.raises(RentalCapacityError) as exc:
            RentalsService.create_rental(
                rental_data(unit, rental_type), user=admin_user
            )
        assert "nenhum registro" in str(exc.value)
        assert Rentals.objects.count() == 0

    def test_null_limit_blocks_creation(
        self, unit, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = None
        rental_type.save(update_fields=["numberOfAppointments"])

        with pytest.raises(RentalCapacityError) as exc:
            RentalsService.create_rental(
                rental_data(unit, rental_type), user=admin_user
            )
        assert "não possui limite" in str(exc.value)
        assert Rentals.objects.count() == 0


@pytest.mark.django_db
class TestRentalUpdate:

    def test_update_sets_updated_by_and_keeps_created_by(
        self, rental_factory, admin_user, other_user
    ):
        rental = rental_factory(created_by=admin_user, updated_by=admin_user)
        updated = RentalsService.update_rental(
            rental,
            {"applicant": "Novo Solicitante"},
            user=other_user,
        )

        updated.refresh_from_db()
        assert updated.applicant == "Novo Solicitante"
        assert updated.created_by == admin_user
        assert updated.updated_by == other_user
        assert updated.status == Rentals.Status.AGENDAMENTO

    def test_update_cannot_override_created_by(
        self, rental_factory, admin_user, other_user
    ):
        rental = rental_factory(created_by=admin_user)
        rental.created_by = other_user

        updated = RentalsService.update_rental(
            rental, {"applicant": "Outro"}, user=other_user
        )

        updated.refresh_from_db()
        assert updated.created_by == admin_user

    def test_update_clears_error_status(
        self, rental_factory, admin_user
    ):
        rental = rental_factory()
        Rentals.objects.filter(pk=rental.pk).update(
            errorStatus="falha anterior"
        )

        updated = RentalsService.update_rental(
            rental, {"applicant": "Corrigido"}, user=admin_user
        )

        updated.refresh_from_db()
        assert updated.errorStatus == ""

    def test_update_ignores_client_status(
        self, rental_factory, admin_user
    ):
        rental = rental_factory()
        updated = RentalsService.update_rental(
            rental,
            {"status": Rentals.Status.FINALIZADO, "applicant": "Teste"},
            user=admin_user,
        )
        assert updated.status == Rentals.Status.AGENDAMENTO

    @pytest.mark.parametrize(
        "status",
        [Rentals.Status.RESERVADO, Rentals.Status.FINALIZADO],
    )
    def test_update_of_non_agendamento_is_blocked(
        self, rental_factory, admin_user, status
    ):
        rental = rental_factory(status=status, errorStatus="")
        with pytest.raises(RentalTransitionError):
            RentalsService.update_rental(
                rental, {"applicant": "Alterado"}, user=admin_user
            )

        rental.refresh_from_db()
        assert rental.applicant == "Solicitante Teste"

    def test_update_excludes_own_record_from_capacity(
        self, rental_factory, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        rental = rental_factory()

        updated = RentalsService.update_rental(
            rental,
            {"applicant": "Ajustado", "endDate": date(2026, 1, 20)},
            user=admin_user,
        )
        assert updated.applicant == "Ajustado"

    def test_update_respects_capacity_of_new_period(
        self, rental_factory, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        rental = rental_factory(endDate=date(2026, 1, 12))
        Rentals.objects.create(
            condominium=rental.condominium,
            typesOfRentals=rental_type,
            startDate=date(2026, 2, 1),
            endDate=date(2026, 2, 5),
            applicant="Outro período",
            charge_amount=False,
        )

        with pytest.raises(RentalCapacityError):
            RentalsService.update_rental(
                rental,
                {
                    "startDate": date(2026, 2, 3),
                    "endDate": date(2026, 2, 4),
                },
                user=admin_user,
            )


@pytest.mark.django_db
class TestReserveRentals:

    def test_reserve_moves_agendamento_to_reservado(
        self, rental_factory, admin_user
    ):
        rental = rental_factory()

        results = RentalsService.reserve_rentals(
            [rental.pk], user=admin_user
        )

        assert results == [{"pk": rental.pk, "success": True, "message": ""}]
        rental.refresh_from_db()
        assert rental.status == Rentals.Status.RESERVADO
        assert rental.updated_by == admin_user
        assert rental.errorStatus == ""

    def test_reserve_clears_previous_error_status(
        self, rental_factory, admin_user
    ):
        rental = rental_factory()
        Rentals.objects.filter(pk=rental.pk).update(errorStatus="erro antigo")

        RentalsService.reserve_rentals([rental.pk], user=admin_user)

        rental.refresh_from_db()
        assert rental.errorStatus == ""

    def test_reserve_rejects_non_agendamento(
        self, rental_factory, admin_user
    ):
        rental = rental_factory(status=Rentals.Status.RESERVADO, errorStatus="")

        results = RentalsService.reserve_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is False
        assert "não permite" in results[0]["message"]
        rental.refresh_from_db()
        assert rental.status == Rentals.Status.RESERVADO
        assert results[0]["message"] in rental.errorStatus

    def test_reserve_rejects_finalized(
        self, rental_factory, admin_user
    ):
        rental = rental_factory(status=Rentals.Status.FINALIZADO)

        results = RentalsService.reserve_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is False
        rental.refresh_from_db()
        assert rental.status == Rentals.Status.FINALIZADO

    def test_reserve_rejects_inactive(
        self, rental_factory, admin_user
    ):
        rental = rental_factory(is_active=False)

        results = RentalsService.reserve_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is False
        assert "inativa" in results[0]["message"]

    def test_reserve_respects_number_of_reservations(
        self, rental_factory, rental_type, admin_user
    ):
        rental_type.numberOfReservations = 1
        rental_type.save(update_fields=["numberOfReservations"])
        first = rental_factory()
        second = rental_factory(applicant="Segundo")

        results = RentalsService.reserve_rentals(
            [first.pk, second.pk], user=admin_user
        )

        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert "Limite de 1 reserva" in results[1]["message"]

        first.refresh_from_db()
        second.refresh_from_db()
        assert first.status == Rentals.Status.RESERVADO
        assert second.status == Rentals.Status.AGENDAMENTO
        assert second.errorStatus == results[1]["message"]

    def test_reserve_does_not_check_appointment_limit(
        self, rental_factory, rental_type, admin_user
    ):
        rental_type.numberOfAppointments = 0
        rental_type.save(update_fields=["numberOfAppointments"])
        rental = rental_factory()

        results = RentalsService.reserve_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is True

    def test_reserve_zero_reservation_limit_blocks(
        self, rental_factory, rental_type, admin_user
    ):
        rental_type.numberOfReservations = 0
        rental_type.save(update_fields=["numberOfReservations"])
        rental = rental_factory()

        results = RentalsService.reserve_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is False
        assert "nenhum registro" in results[0]["message"]

    def test_reserve_null_reservation_limit_blocks(
        self, rental_factory, rental_type, admin_user
    ):
        rental_type.numberOfReservations = None
        rental_type.save(update_fields=["numberOfReservations"])
        rental = rental_factory()

        results = RentalsService.reserve_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is False
        assert "não possui limite" in results[0]["message"]

    def test_reserve_counts_only_reserved_in_same_scope(
        self, rental_factory, rental_type, other_unit, admin_user
    ):
        rental_type.numberOfReservations = 1
        rental_type.save(update_fields=["numberOfReservations"])
        rental_factory(
            status=Rentals.Status.RESERVADO, condominium=other_unit
        )
        rental = rental_factory()

        results = RentalsService.reserve_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is True

    def test_partial_success_in_batch(
        self, rental_factory, admin_user
    ):
        eligible = rental_factory()
        finalized = rental_factory(status=Rentals.Status.FINALIZADO)

        results = RentalsService.reserve_rentals(
            [eligible.pk, finalized.pk], user=admin_user
        )

        by_pk = {item["pk"]: item for item in results}
        assert by_pk[eligible.pk]["success"] is True
        assert by_pk[finalized.pk]["success"] is False

        eligible.refresh_from_db()
        finalized.refresh_from_db()
        assert eligible.status == Rentals.Status.RESERVADO
        assert finalized.status == Rentals.Status.FINALIZADO
        assert finalized.errorStatus

    def test_missing_rental_is_reported(self, admin_user):
        results = RentalsService.reserve_rentals([999999], user=admin_user)
        assert results[0]["success"] is False
        assert results[0]["message"] == "Locação não encontrada."


@pytest.mark.django_db
class TestFinalizeRentals:

    def test_finalize_reserved(self, rental_factory, admin_user):
        rental = rental_factory(status=Rentals.Status.RESERVADO)

        results = RentalsService.finalize_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is True
        rental.refresh_from_db()
        assert rental.status == Rentals.Status.FINALIZADO
        assert rental.updated_by == admin_user

    def test_finalize_rejects_agendamento(
        self, rental_factory, admin_user
    ):
        rental = rental_factory()

        results = RentalsService.finalize_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is False
        assert "É necessário estar em 'Reservado'" in results[0]["message"]
        rental.refresh_from_db()
        assert rental.status == Rentals.Status.AGENDAMENTO
        assert rental.errorStatus == results[0]["message"]

    def test_finalize_is_not_repeatable(
        self, rental_factory, admin_user
    ):
        rental = rental_factory(status=Rentals.Status.FINALIZADO)

        results = RentalsService.finalize_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is False
        rental.refresh_from_db()
        assert rental.status == Rentals.Status.FINALIZADO

    def test_finalize_does_not_apply_capacity_limits(
        self, rental_factory, rental_type, admin_user
    ):
        rental_type.numberOfReservations = 0
        rental_type.numberOfAppointments = 0
        rental_type.save(
            update_fields=["numberOfReservations", "numberOfAppointments"]
        )
        rental = rental_factory(status=Rentals.Status.RESERVADO)

        results = RentalsService.finalize_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is True

    def test_finalize_rejects_inactive(
        self, rental_factory, admin_user
    ):
        rental = rental_factory(
            status=Rentals.Status.RESERVADO, is_active=False
        )

        results = RentalsService.finalize_rentals(
            [rental.pk], user=admin_user
        )

        assert results[0]["success"] is False
        assert "inativa" in results[0]["message"]

    def test_finalize_clears_previous_error_status(
        self, rental_factory, admin_user
    ):
        rental = rental_factory(status=Rentals.Status.RESERVADO)
        Rentals.objects.filter(pk=rental.pk).update(errorStatus="erro antigo")

        RentalsService.finalize_rentals([rental.pk], user=admin_user)

        rental.refresh_from_db()
        assert rental.errorStatus == ""
