from datetime import date

import pytest

from domains.reservations.exceptions import (
    MoveReservationTransitionError,
    MoveReservationValidationError,
)
from domains.reservations.models import MoveReservations
from domains.reservations.services.move_reservations_service import (
    MoveReservationsService,
)


def move_data(unit, **overrides):
    data = {
        "condominium": unit,
        "typeOfChange": "E",
        "startDate": date(2026, 11, 10),
        "endDate": date(2026, 11, 12),
        "applicant": "  Maria Souza  ",
        "observations": "  Observação  ",
        "is_active": True,
    }
    data.update(overrides)
    return data


def move_factory(
    unit,
    *,
    status=MoveReservations.Status.AGENDAMENTO,
    created_by=None,
    **overrides,
):
    data = move_data(unit, **overrides)
    data["status"] = status
    data["created_by"] = created_by
    return MoveReservations.objects.create(**data)


@pytest.mark.django_db
class TestMoveReservationCreate:

    def test_create_sets_initial_status_and_audit(self, unit, admin_user):
        move = MoveReservationsService.create_move(
            move_data(unit), user=admin_user
        )

        assert move.pk is not None
        assert move.status == MoveReservations.Status.AGENDAMENTO
        assert move.created_by == admin_user
        assert move.updated_by == admin_user
        assert move.applicant == "Maria Souza"
        assert move.observations == "Observação"
        assert move.typeOfChange == "E"

    def test_create_ignores_client_status_and_audit(
        self, unit, admin_user, other_user
    ):
        data = move_data(unit)
        data.update(
            {
                "status": MoveReservations.Status.FINALIZADO,
                "created_by": other_user,
                "updated_by": other_user,
            }
        )

        move = MoveReservationsService.create_move(data, user=admin_user)

        assert move.status == MoveReservations.Status.AGENDAMENTO
        assert move.created_by == admin_user
        assert move.updated_by == admin_user

    def test_create_without_user_leaves_audit_empty(self, unit):
        move = MoveReservationsService.create_move(move_data(unit))
        assert move.created_by is None
        assert move.updated_by is None

    def test_create_normalizes_string_booleans(self, unit, admin_user):
        move = MoveReservationsService.create_move(
            move_data(unit, is_active="off"), user=admin_user
        )
        assert move.is_active is False

    def test_create_requires_unit(self, admin_user):
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.create_move(
                move_data(None), user=admin_user
            )

    def test_create_requires_type(self, unit, admin_user):
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.create_move(
                move_data(unit, typeOfChange=None), user=admin_user
            )

    def test_create_rejects_invalid_type(self, unit, admin_user):
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.create_move(
                move_data(unit, typeOfChange="X"), user=admin_user
            )

    def test_create_requires_end_date(self, unit, admin_user):
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.create_move(
                move_data(unit, endDate=None), user=admin_user
            )

    def test_create_rejects_end_before_start(self, unit, admin_user):
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.create_move(
                move_data(
                    unit,
                    startDate=date(2026, 11, 15),
                    endDate=date(2026, 11, 10),
                ),
                user=admin_user,
            )

    def test_create_requires_applicant(self, unit, admin_user):
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.create_move(
                move_data(unit, applicant="   "), user=admin_user
            )


@pytest.mark.django_db
class TestMoveReservationUpdate:

    def test_update_allowed_in_agendamento(
        self, unit, admin_user, other_user
    ):
        move = move_factory(unit, created_by=admin_user)
        updated = MoveReservationsService.update_move(
            move,
            {
                "applicant": "Maria Alterada",
                "endDate": date(2026, 11, 13),
                "typeOfChange": "S",
            },
            user=other_user,
        )

        assert updated.applicant == "Maria Alterada"
        assert updated.endDate == date(2026, 11, 13)
        assert updated.typeOfChange == "S"
        assert updated.created_by == admin_user
        assert updated.updated_by == other_user

    def test_update_ignores_forged_status_and_created_by(
        self, unit, admin_user, other_user
    ):
        move = move_factory(unit, created_by=admin_user)
        updated = MoveReservationsService.update_move(
            move,
            {
                "applicant": "Maria Alterada",
                "status": MoveReservations.Status.FINALIZADO,
                "created_by": other_user,
            },
            user=other_user,
        )

        assert updated.status == MoveReservations.Status.AGENDAMENTO
        assert updated.created_by == admin_user

    def test_update_blocked_in_execution(self, unit, admin_user):
        move = move_factory(
            unit,
            status=MoveReservations.Status.EXECUCAO,
            created_by=admin_user,
        )
        with pytest.raises(MoveReservationTransitionError):
            MoveReservationsService.update_move(
                move, {"applicant": "Maria Alterada"}, user=admin_user
            )
        move.refresh_from_db()
        assert move.applicant != "Maria Alterada"

    def test_update_blocked_in_finalized(self, unit, admin_user):
        move = move_factory(
            unit,
            status=MoveReservations.Status.FINALIZADO,
            created_by=admin_user,
        )
        with pytest.raises(MoveReservationTransitionError):
            MoveReservationsService.update_move(
                move, {"applicant": "Maria Alterada"}, user=admin_user
            )

    def test_update_missing_instance_raises(self, admin_user):
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.update_move(
                None, {"applicant": "Maria"}, user=admin_user
            )

    def test_update_rejects_invalid_period(self, unit, admin_user):
        move = move_factory(unit)
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.update_move(
                move,
                {
                    "startDate": date(2026, 11, 20),
                    "endDate": date(2026, 11, 10),
                },
                user=admin_user,
            )

    def test_update_rejects_invalid_type(self, unit, admin_user):
        move = move_factory(unit)
        with pytest.raises(MoveReservationValidationError):
            MoveReservationsService.update_move(
                move, {"typeOfChange": "X"}, user=admin_user
            )


@pytest.mark.django_db
class TestMoveReservationTransitions:

    def test_execute_changes_agendamento_to_execucao(
        self, unit, admin_user
    ):
        move = move_factory(unit, created_by=admin_user)
        results = MoveReservationsService.execute_moves(
            [move.pk], user=admin_user
        )

        assert results == [
            {"pk": move.pk, "success": True, "message": ""}
        ]
        move.refresh_from_db()
        assert move.status == MoveReservations.Status.EXECUCAO
        assert move.updated_by == admin_user
        assert move.created_by == admin_user

    def test_finalize_changes_execucao_to_finalizado(
        self, unit, admin_user
    ):
        move = move_factory(
            unit,
            status=MoveReservations.Status.EXECUCAO,
            created_by=admin_user,
        )
        results = MoveReservationsService.finalize_moves(
            [move.pk], user=admin_user
        )

        assert results[0]["success"] is True
        move.refresh_from_db()
        assert move.status == MoveReservations.Status.FINALIZADO
        assert move.updated_by == admin_user

    def test_execute_rejects_finalized(self, unit, admin_user):
        move = move_factory(
            unit, status=MoveReservations.Status.FINALIZADO
        )
        results = MoveReservationsService.execute_moves(
            [move.pk], user=admin_user
        )

        assert results[0]["success"] is False
        move.refresh_from_db()
        assert move.status == MoveReservations.Status.FINALIZADO

    def test_execute_rejects_execucao(self, unit, admin_user):
        move = move_factory(unit, status=MoveReservations.Status.EXECUCAO)
        results = MoveReservationsService.execute_moves(
            [move.pk], user=admin_user
        )
        assert results[0]["success"] is False

    def test_finalize_rejects_agendamento(self, unit, admin_user):
        move = move_factory(unit)
        results = MoveReservationsService.finalize_moves(
            [move.pk], user=admin_user
        )

        assert results[0]["success"] is False
        move.refresh_from_db()
        assert move.status == MoveReservations.Status.AGENDAMENTO

    def test_finalize_rejects_finalizado(self, unit, admin_user):
        move = move_factory(
            unit, status=MoveReservations.Status.FINALIZADO
        )
        results = MoveReservationsService.finalize_moves(
            [move.pk], user=admin_user
        )
        assert results[0]["success"] is False

    def test_transition_rejects_missing_id(self, admin_user):
        results = MoveReservationsService.execute_moves(
            [999999], user=admin_user
        )
        assert results[0]["success"] is False
        assert results[0]["message"] == "Mudança não encontrada."

    def test_batch_allows_partial_success(self, unit, admin_user):
        agendada = move_factory(unit)
        finalizada = move_factory(
            unit, status=MoveReservations.Status.FINALIZADO
        )
        results = MoveReservationsService.execute_moves(
            [agendada.pk, finalizada.pk], user=admin_user
        )

        assert len(results) == 2
        by_pk = {item["pk"]: item for item in results}
        assert by_pk[agendada.pk]["success"] is True
        assert by_pk[finalizada.pk]["success"] is False

        agendada.refresh_from_db()
        finalizada.refresh_from_db()
        assert agendada.status == MoveReservations.Status.EXECUCAO
        assert finalizada.status == MoveReservations.Status.FINALIZADO

    def test_batch_message_identifies_rejected_reason(
        self, unit, admin_user
    ):
        move = move_factory(
            unit, status=MoveReservations.Status.FINALIZADO
        )
        results = MoveReservationsService.finalize_moves(
            [move.pk], user=admin_user
        )
        message = results[0]["message"]
        assert "Finalizado" in message
        assert "Execução" in message

    def test_transition_without_user_keeps_updated_by_empty(self, unit):
        move = move_factory(unit)
        MoveReservationsService.execute_moves([move.pk])
        move.refresh_from_db()
        assert move.status == MoveReservations.Status.EXECUCAO
        assert move.updated_by is None
