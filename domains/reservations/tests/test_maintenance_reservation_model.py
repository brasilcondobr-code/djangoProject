from datetime import date

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from domains.reservations.models import MaintenanceReservations
from domains.reservations.validators.maintenance_reservations_validators import (
    APPLICANT_MAX_LENGTH,
)


def maintenance_data(unit, maintenance_type, **overrides):
    data = {
        "condominium": unit,
        "typesOfMaintenance": maintenance_type,
        "startDate": date(2026, 11, 10),
        "endDate": date(2026, 11, 12),
        "applicant": "Maria Souza",
        "observations": "",
        "is_active": True,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestMaintenanceReservationsModel:

    def test_create_valid(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        assert maintenance.pk is not None
        assert maintenance.condominium == unit
        assert maintenance.typesOfMaintenance == maintenance_type
        assert maintenance.startDate == date(2026, 11, 10)
        assert maintenance.endDate == date(2026, 11, 12)

    def test_default_status_is_agendamento(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        assert maintenance.status == MaintenanceReservations.Status.AGENDAMENTO
        assert maintenance.status == "agendamento"

    def test_default_is_active_true(self, unit, maintenance_type):
        data = maintenance_data(unit, maintenance_type)
        data.pop("is_active")
        maintenance = MaintenanceReservations.objects.create(**data)
        assert maintenance.is_active is True

    def test_observations_default_empty(self, unit, maintenance_type):
        data = maintenance_data(unit, maintenance_type)
        data.pop("observations")
        maintenance = MaintenanceReservations.objects.create(**data)
        assert maintenance.observations == ""

    def test_created_at_and_updated_at_filled(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        assert maintenance.created_at is not None
        assert maintenance.updated_at is not None

    def test_updated_at_changes_on_update(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        original_updated = maintenance.updated_at
        maintenance.applicant = "Maria Souza Alterada"
        maintenance.save()
        maintenance.refresh_from_db()
        assert maintenance.updated_at >= original_updated

    def test_str_returns_identifier(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        assert str(maintenance) == (
            f"02. Manutenção {maintenance.pk} - Maria Souza"
        )

    def test_str_without_applicant(self):
        assert str(MaintenanceReservations()) == (
            "02. Manutenção - sem solicitante"
        )

    def test_end_date_before_start_date_raises(self, unit, maintenance_type):
        with pytest.raises(IntegrityError):
            MaintenanceReservations.objects.create(
                **maintenance_data(
                    unit,
                    maintenance_type,
                    startDate=date(2026, 11, 15),
                    endDate=date(2026, 11, 10),
                )
            )

    def test_end_date_equal_start_date_allowed(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(
                unit,
                maintenance_type,
                startDate=date(2026, 11, 10),
                endDate=date(2026, 11, 10),
            )
        )
        assert maintenance.pk is not None

    def test_condominium_required(self, maintenance_type):
        with pytest.raises(IntegrityError):
            MaintenanceReservations.objects.create(
                **maintenance_data(
                    None,
                    maintenance_type,
                    condominium=None,
                )
            )

    def test_types_of_maintenance_required(self, unit):
        with pytest.raises(IntegrityError):
            MaintenanceReservations.objects.create(
                **maintenance_data(
                    unit,
                    None,
                    typesOfMaintenance=None,
                )
            )

    def test_applicant_required(self, unit, maintenance_type):
        with pytest.raises(IntegrityError):
            MaintenanceReservations.objects.create(
                **maintenance_data(unit, maintenance_type, applicant=None)
            )

    def test_fields_configuration(self):
        field = MaintenanceReservations._meta.get_field("applicant")
        assert field.max_length == APPLICANT_MAX_LENGTH == 255
        assert field.blank is False
        assert field.null is False

        start = MaintenanceReservations._meta.get_field("startDate")
        end = MaintenanceReservations._meta.get_field("endDate")
        assert start.blank is False and start.null is False
        assert end.blank is False and end.null is False

        observations = MaintenanceReservations._meta.get_field("observations")
        assert observations.blank is True

    def test_audit_fields_not_editable(self):
        for name in (
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ):
            assert MaintenanceReservations._meta.get_field(name).editable is False

    def test_created_by_and_updated_by_nullable(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        assert maintenance.created_by is None
        assert maintenance.updated_by is None

    def test_related_name_on_unit(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        assert list(unit.maintenance_reservations.all()) == [maintenance]

    def test_related_name_on_type(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        assert list(maintenance_type.maintenance_reservations.all()) == [
            maintenance
        ]

    def test_deleting_unit_with_maintenance_is_protected(
        self, unit, maintenance_type
    ):
        MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        with pytest.raises(ProtectedError):
            unit.delete()

    def test_deleting_type_with_maintenance_is_protected(
        self, unit, maintenance_type
    ):
        MaintenanceReservations.objects.create(
            **maintenance_data(unit, maintenance_type)
        )
        with pytest.raises(ProtectedError):
            maintenance_type.delete()

    def test_verbose_names(self):
        assert MaintenanceReservations._meta.verbose_name == "02. Manutenção"
        assert (
            MaintenanceReservations._meta.verbose_name_plural
            == "02. Manutenções"
        )

    def test_ordering(self, unit, maintenance_type):
        first = MaintenanceReservations.objects.create(
            **maintenance_data(
                unit,
                maintenance_type,
                startDate=date(2026, 11, 10),
                endDate=date(2026, 11, 11),
            )
        )
        second = MaintenanceReservations.objects.create(
            **maintenance_data(
                unit,
                maintenance_type,
                startDate=date(2026, 12, 10),
                endDate=date(2026, 12, 11),
            )
        )
        assert list(MaintenanceReservations.objects.all()) == [second, first]

    def test_period_constraint_name(self):
        names = [
            constraint.name
            for constraint in MaintenanceReservations._meta.constraints
        ]
        assert names == ["maintenance_reservations_end_date_gte_start_date"]
