from datetime import date

import pytest

from domains.reservations.exceptions import (
    MaintenanceReservationTransitionError,
    MaintenanceReservationValidationError,
)
from domains.reservations.models import MaintenanceReservations
from domains.reservations.services.maintenance_reservations_service import (
    MaintenanceReservationsService,
)


def maintenance_data(unit, maintenance_type, **overrides):
    data = {
        "condominium": unit,
        "typesOfMaintenance": maintenance_type,
        "startDate": date(2026, 11, 10),
        "endDate": date(2026, 11, 12),
        "applicant": "  Maria Souza  ",
        "observations": "  Observação  ",
        "is_active": True,
    }
    data.update(overrides)
    return data


def maintenance_factory(
    unit,
    maintenance_type,
    *,
    status=MaintenanceReservations.Status.AGENDAMENTO,
    created_by=None,
    **overrides,
):
    data = maintenance_data(unit, maintenance_type, **overrides)
    data["status"] = status
    data["created_by"] = created_by
    return MaintenanceReservations.objects.create(**data)


@pytest.mark.django_db
class TestMaintenanceReservationCreate:

    def test_create_sets_initial_status_and_audit(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = MaintenanceReservationsService.create_maintenance(
            maintenance_data(unit, maintenance_type), user=admin_user
        )

        assert maintenance.pk is not None
        assert maintenance.status == MaintenanceReservations.Status.AGENDAMENTO
        assert maintenance.created_by == admin_user
        assert maintenance.updated_by == admin_user
        assert maintenance.applicant == "Maria Souza"
        assert maintenance.observations == "Observação"

    def test_create_ignores_client_status_and_audit(
        self, unit, maintenance_type, admin_user, other_user
    ):
        data = maintenance_data(unit, maintenance_type)
        data.update(
            {
                "status": MaintenanceReservations.Status.FINALIZADO,
                "created_by": other_user,
                "updated_by": other_user,
            }
        )

        maintenance = MaintenanceReservationsService.create_maintenance(
            data, user=admin_user
        )

        assert maintenance.status == MaintenanceReservations.Status.AGENDAMENTO
        assert maintenance.created_by == admin_user
        assert maintenance.updated_by == admin_user

    def test_create_without_user_leaves_audit_empty(
        self, unit, maintenance_type
    ):
        maintenance = MaintenanceReservationsService.create_maintenance(
            maintenance_data(unit, maintenance_type)
        )
        assert maintenance.created_by is None
        assert maintenance.updated_by is None

    def test_create_normalizes_string_booleans(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = MaintenanceReservationsService.create_maintenance(
            maintenance_data(unit, maintenance_type, is_active="off"),
            user=admin_user,
        )
        assert maintenance.is_active is False

    def test_create_requires_unit(self, maintenance_type, admin_user):
        with pytest.raises(MaintenanceReservationValidationError):
            MaintenanceReservationsService.create_maintenance(
                maintenance_data(None, maintenance_type),
                user=admin_user,
            )

    def test_create_requires_type(self, unit, admin_user):
        with pytest.raises(MaintenanceReservationValidationError):
            MaintenanceReservationsService.create_maintenance(
                maintenance_data(unit, None),
                user=admin_user,
            )

    def test_create_requires_end_date(self, unit, maintenance_type, admin_user):
        with pytest.raises(MaintenanceReservationValidationError):
            MaintenanceReservationsService.create_maintenance(
                maintenance_data(unit, maintenance_type, endDate=None),
                user=admin_user,
            )

    def test_create_rejects_end_before_start(
        self, unit, maintenance_type, admin_user
    ):
        with pytest.raises(MaintenanceReservationValidationError):
            MaintenanceReservationsService.create_maintenance(
                maintenance_data(
                    unit,
                    maintenance_type,
                    startDate=date(2026, 11, 15),
                    endDate=date(2026, 11, 10),
                ),
                user=admin_user,
            )

    def test_create_requires_applicant(
        self, unit, maintenance_type, admin_user
    ):
        with pytest.raises(MaintenanceReservationValidationError):
            MaintenanceReservationsService.create_maintenance(
                maintenance_data(unit, maintenance_type, applicant="   "),
                user=admin_user,
            )


@pytest.mark.django_db
class TestMaintenanceReservationUpdate:

    def test_update_allowed_in_agendamento(
        self, unit, maintenance_type, admin_user, other_user
    ):
        maintenance = maintenance_factory(
            unit, maintenance_type, created_by=admin_user
        )
        updated = MaintenanceReservationsService.update_maintenance(
            maintenance,
            {"applicant": "Maria Alterada", "endDate": date(2026, 11, 13)},
            user=other_user,
        )

        assert updated.applicant == "Maria Alterada"
        assert updated.endDate == date(2026, 11, 13)
        assert updated.created_by == admin_user
        assert updated.updated_by == other_user

    def test_update_ignores_forged_status_and_created_by(
        self, unit, maintenance_type, admin_user, other_user
    ):
        maintenance = maintenance_factory(
            unit, maintenance_type, created_by=admin_user
        )
        updated = MaintenanceReservationsService.update_maintenance(
            maintenance,
            {
                "applicant": "Maria Alterada",
                "status": MaintenanceReservations.Status.FINALIZADO,
                "created_by": other_user,
            },
            user=other_user,
        )

        assert updated.status == MaintenanceReservations.Status.AGENDAMENTO
        assert updated.created_by == admin_user

    def test_update_blocked_in_execution(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.EXECUCAO,
            created_by=admin_user,
        )
        with pytest.raises(MaintenanceReservationTransitionError):
            MaintenanceReservationsService.update_maintenance(
                maintenance,
                {"applicant": "Maria Alterada"},
                user=admin_user,
            )
        maintenance.refresh_from_db()
        assert maintenance.applicant != "Maria Alterada"

    def test_update_blocked_in_finalized(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
            created_by=admin_user,
        )
        with pytest.raises(MaintenanceReservationTransitionError):
            MaintenanceReservationsService.update_maintenance(
                maintenance,
                {"applicant": "Maria Alterada"},
                user=admin_user,
            )

    def test_update_missing_instance_raises(self, admin_user):
        with pytest.raises(MaintenanceReservationValidationError):
            MaintenanceReservationsService.update_maintenance(
                None, {"applicant": "Maria"}, user=admin_user
            )

    def test_update_rejects_invalid_period(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(unit, maintenance_type)
        with pytest.raises(MaintenanceReservationValidationError):
            MaintenanceReservationsService.update_maintenance(
                maintenance,
                {
                    "startDate": date(2026, 11, 20),
                    "endDate": date(2026, 11, 10),
                },
                user=admin_user,
            )


@pytest.mark.django_db
class TestMaintenanceReservationTransitions:

    def test_execute_changes_agendamento_to_execucao(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(
            unit, maintenance_type, created_by=admin_user
        )
        results = MaintenanceReservationsService.execute_maintenances(
            [maintenance.pk], user=admin_user
        )

        assert results == [{"pk": maintenance.pk, "success": True, "message": ""}]
        maintenance.refresh_from_db()
        assert maintenance.status == MaintenanceReservations.Status.EXECUCAO
        assert maintenance.updated_by == admin_user
        assert maintenance.created_by == admin_user

    def test_finalize_changes_execucao_to_finalizado(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.EXECUCAO,
            created_by=admin_user,
        )
        results = MaintenanceReservationsService.finalize_maintenances(
            [maintenance.pk], user=admin_user
        )

        assert results[0]["success"] is True
        maintenance.refresh_from_db()
        assert maintenance.status == MaintenanceReservations.Status.FINALIZADO
        assert maintenance.updated_by == admin_user

    def test_execute_rejects_finalized(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        results = MaintenanceReservationsService.execute_maintenances(
            [maintenance.pk], user=admin_user
        )

        assert results[0]["success"] is False
        assert "#" not in results[0]["message"]
        maintenance.refresh_from_db()
        assert maintenance.status == MaintenanceReservations.Status.FINALIZADO

    def test_execute_rejects_execucao(self, unit, maintenance_type, admin_user):
        maintenance = maintenance_factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.EXECUCAO,
        )
        results = MaintenanceReservationsService.execute_maintenances(
            [maintenance.pk], user=admin_user
        )
        assert results[0]["success"] is False

    def test_finalize_rejects_agendamento(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(unit, maintenance_type)
        results = MaintenanceReservationsService.finalize_maintenances(
            [maintenance.pk], user=admin_user
        )

        assert results[0]["success"] is False
        maintenance.refresh_from_db()
        assert maintenance.status == MaintenanceReservations.Status.AGENDAMENTO

    def test_finalize_rejects_finalizado(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        results = MaintenanceReservationsService.finalize_maintenances(
            [maintenance.pk], user=admin_user
        )
        assert results[0]["success"] is False

    def test_transition_rejects_missing_id(self, admin_user):
        results = MaintenanceReservationsService.execute_maintenances(
            [999999], user=admin_user
        )
        assert results[0]["success"] is False
        assert results[0]["message"] == "Manutenção não encontrada."

    def test_batch_allows_partial_success(
        self, unit, maintenance_type, admin_user
    ):
        agendada = maintenance_factory(unit, maintenance_type)
        finalizada = maintenance_factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        results = MaintenanceReservationsService.execute_maintenances(
            [agendada.pk, finalizada.pk], user=admin_user
        )

        assert len(results) == 2
        by_pk = {item["pk"]: item for item in results}
        assert by_pk[agendada.pk]["success"] is True
        assert by_pk[finalizada.pk]["success"] is False

        agendada.refresh_from_db()
        finalizada.refresh_from_db()
        assert agendada.status == MaintenanceReservations.Status.EXECUCAO
        assert finalizada.status == MaintenanceReservations.Status.FINALIZADO

    def test_batch_message_identifies_rejected_reason(
        self, unit, maintenance_type, admin_user
    ):
        maintenance = maintenance_factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        results = MaintenanceReservationsService.finalize_maintenances(
            [maintenance.pk], user=admin_user
        )
        message = results[0]["message"]
        assert "Finalizado" in message
        assert "Execução" in message

    def test_transition_without_user_keeps_updated_by_empty(
        self, unit, maintenance_type
    ):
        maintenance = maintenance_factory(unit, maintenance_type)
        MaintenanceReservationsService.execute_maintenances([maintenance.pk])
        maintenance.refresh_from_db()
        assert maintenance.status == MaintenanceReservations.Status.EXECUCAO
        assert maintenance.updated_by is None
