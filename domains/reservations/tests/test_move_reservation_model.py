from datetime import date

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from domains.reservations.models import MoveReservations
from domains.reservations.validators.move_reservations_validators import (
    APPLICANT_MAX_LENGTH,
)


def move_data(unit, **overrides):
    data = {
        "condominium": unit,
        "typeOfChange": MoveReservations.TypeOfChange.ENTRADA,
        "startDate": date(2026, 11, 10),
        "endDate": date(2026, 11, 12),
        "applicant": "Maria Souza",
        "observations": "",
        "is_active": True,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestMoveReservationsModel:

    def test_create_valid(self, unit):
        move = MoveReservations.objects.create(**move_data(unit))
        assert move.pk is not None
        assert move.condominium == unit
        assert move.typeOfChange == MoveReservations.TypeOfChange.ENTRADA
        assert move.startDate == date(2026, 11, 10)
        assert move.endDate == date(2026, 11, 12)

    def test_type_of_change_choices(self):
        assert MoveReservations.TypeOfChange.ENTRADA == "E"
        assert MoveReservations.TypeOfChange.SAIDA == "S"
        assert MoveReservations.TypeOfChange.choices == [
            ("E", "Entrada"),
            ("S", "Saída"),
        ]

    def test_default_status_is_agendamento(self, unit):
        move = MoveReservations.objects.create(**move_data(unit))
        assert move.status == MoveReservations.Status.AGENDAMENTO
        assert move.status == "agendamento"

    def test_default_is_active_true(self, unit):
        data = move_data(unit)
        data.pop("is_active")
        move = MoveReservations.objects.create(**data)
        assert move.is_active is True

    def test_observations_default_empty(self, unit):
        data = move_data(unit)
        data.pop("observations")
        move = MoveReservations.objects.create(**data)
        assert move.observations == ""

    def test_created_at_and_updated_at_filled(self, unit):
        move = MoveReservations.objects.create(**move_data(unit))
        assert move.created_at is not None
        assert move.updated_at is not None

    def test_updated_at_changes_on_update(self, unit):
        move = MoveReservations.objects.create(**move_data(unit))
        original_updated = move.updated_at
        move.applicant = "Maria Souza Alterada"
        move.save()
        move.refresh_from_db()
        assert move.updated_at >= original_updated

    def test_str_returns_identifier(self, unit):
        move = MoveReservations.objects.create(**move_data(unit))
        assert str(move) == f"03. Mudança {move.pk} - Maria Souza"

    def test_str_without_applicant(self):
        assert str(MoveReservations()) == "03. Mudança - sem solicitante"

    def test_end_date_before_start_date_raises(self, unit):
        with pytest.raises(IntegrityError):
            MoveReservations.objects.create(
                **move_data(
                    unit,
                    startDate=date(2026, 11, 15),
                    endDate=date(2026, 11, 10),
                )
            )

    def test_end_date_equal_start_date_allowed(self, unit):
        move = MoveReservations.objects.create(
            **move_data(
                unit,
                startDate=date(2026, 11, 10),
                endDate=date(2026, 11, 10),
            )
        )
        assert move.pk is not None

    def test_condominium_required(self):
        with pytest.raises(IntegrityError):
            MoveReservations.objects.create(**move_data(None))

    def test_type_of_change_required(self, unit):
        with pytest.raises(IntegrityError):
            MoveReservations.objects.create(**move_data(unit, typeOfChange=None))

    def test_applicant_required(self, unit):
        with pytest.raises(IntegrityError):
            MoveReservations.objects.create(**move_data(unit, applicant=None))

    def test_fields_configuration(self):
        field = MoveReservations._meta.get_field("applicant")
        assert field.max_length == APPLICANT_MAX_LENGTH == 255
        assert field.blank is False
        assert field.null is False

        type_field = MoveReservations._meta.get_field("typeOfChange")
        assert type_field.max_length == 1
        assert type_field.blank is False
        assert type_field.null is False
        assert type_field.choices == [("E", "Entrada"), ("S", "Saída")]

        start = MoveReservations._meta.get_field("startDate")
        end = MoveReservations._meta.get_field("endDate")
        assert start.blank is False and start.null is False
        assert end.blank is False and end.null is False

        observations = MoveReservations._meta.get_field("observations")
        assert observations.blank is True

    def test_audit_fields_not_editable(self):
        for name in (
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ):
            assert MoveReservations._meta.get_field(name).editable is False

    def test_created_by_and_updated_by_nullable(self, unit):
        move = MoveReservations.objects.create(**move_data(unit))
        assert move.created_by is None
        assert move.updated_by is None

    def test_related_name_on_unit(self, unit):
        move = MoveReservations.objects.create(**move_data(unit))
        assert list(unit.move_reservations.all()) == [move]

    def test_deleting_unit_with_move_is_protected(self, unit):
        MoveReservations.objects.create(**move_data(unit))
        with pytest.raises(ProtectedError):
            unit.delete()

    def test_verbose_names(self):
        assert MoveReservations._meta.verbose_name == "03. Mudança"
        assert MoveReservations._meta.verbose_name_plural == "03. Mudanças"

    def test_ordering(self, unit):
        first = MoveReservations.objects.create(
            **move_data(
                unit,
                startDate=date(2026, 11, 10),
                endDate=date(2026, 11, 11),
            )
        )
        second = MoveReservations.objects.create(
            **move_data(
                unit,
                startDate=date(2026, 12, 10),
                endDate=date(2026, 12, 11),
            )
        )
        assert list(MoveReservations.objects.all()) == [second, first]

    def test_period_constraint_name(self):
        names = [c.name for c in MoveReservations._meta.constraints]
        assert names == ["move_reservations_end_date_gte_start_date"]
