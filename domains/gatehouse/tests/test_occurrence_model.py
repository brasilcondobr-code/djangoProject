from datetime import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.timezone import make_aware

from domains.condominium.models import Collaborator
from domains.gatehouse.models import Occurrence

pytestmark = pytest.mark.django_db


class TestOccurrenceModel:

    @pytest.fixture
    def occurrence(self, unit):
        return Occurrence.objects.create(
            unit=unit,
            releaseDate=make_aware(datetime(2026, 10, 5, 14, 30)),
            subject="Barulho na área comum",
            description="Reclamação de moradores",
        )

    def test_create_and_str(self, occurrence):
        assert occurrence.pk is not None
        assert str(occurrence) == "Ocorrência Barulho na área comum"

    def test_str_without_subject_falls_back(self):
        assert str(Occurrence()) == "07. Ocorrência"

    def test_meta_verbose(self):
        assert str(Occurrence._meta.verbose_name) == "07. Ocorrência"
        assert str(Occurrence._meta.verbose_name_plural) == "07. Ocorrências"
        assert Occurrence._meta.app_label == "gatehouse"

    def test_ordering(self):
        assert Occurrence._meta.ordering == ["-releaseDate", "-id"]

    def test_unique_constraint(self):
        constraint = Occurrence._meta.constraints[0]
        assert constraint.name == "uniq_occurrence_unit_date_subject"
        assert tuple(constraint.fields) == ("unit", "releaseDate", "subject")

    def test_duplicate_triple_blocked_by_db(self, unit):
        data = dict(
            unit=unit,
            releaseDate=make_aware(datetime(2026, 10, 5, 9, 0)),
            subject="Tripla repetida",
        )
        Occurrence.objects.create(**data)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Occurrence.objects.create(**data)

    def test_null_unit_allows_same_date_and_subject(self, unit):
        """Decisão: NULLs são distintos no PostgreSQL (padrão módulo 04)."""
        release = make_aware(datetime(2026, 10, 5, 9, 0))
        Occurrence.objects.create(
            unit=None, releaseDate=release, subject="Sem unidade"
        )
        second = Occurrence.objects.create(
            unit=None, releaseDate=release, subject="Sem unidade"
        )
        assert second.pk is not None

    def test_different_subject_same_slot_allowed(self, unit):
        release = make_aware(datetime(2026, 10, 5, 9, 0))
        Occurrence.objects.create(unit=unit, releaseDate=release, subject="A")
        second = Occurrence.objects.create(
            unit=unit, releaseDate=release, subject="B"
        )
        assert second.pk is not None

    def test_field_rules(self):
        get = Occurrence._meta.get_field
        assert get("unit").null is True
        assert get("unit").blank is True
        assert get("unit").remote_field.related_name == "occurrences"
        assert get("releaseDate").null is True
        assert get("releaseDate").blank is True
        assert get("subject").null is False
        assert get("subject").max_length == 255
        assert get("participants").blank is True
        assert get("participants").remote_field.related_name == "occurrences"
        assert get("description").null is True
        assert get("is_active").default is True
        assert get("created_user").editable is False
        assert get("created_user").null is True
        assert get("created_at").auto_now_add is True
        assert get("updated_at").auto_now is True

    def test_participants_accessor(self, occurrence, participant_a, participant_b):
        occurrence.participants.add(participant_a, participant_b)
        names = set(occurrence.participants.values_list("name", flat=True))
        assert names == {"Participante A", "Participante B"}
        assert set(participant_a.occurrences.all()) == {occurrence}

    def test_default_is_active_and_audit_null_without_user(self, unit):
        occurrence = Occurrence.objects.create(
            unit=unit, subject="Sem auditoria"
        )
        assert occurrence.is_active is True
        assert occurrence.created_user is None
        assert occurrence.releaseDate is None
        assert occurrence.participants.count() == 0

    def test_reverse_relation_from_unit(self, occurrence, unit):
        assert list(unit.occurrences.all()) == [occurrence]

    def test_reverse_relation_from_collaborator(self, occurrence, participant_a):
        occurrence.participants.add(participant_a)
        assert list(participant_a.occurrences.all()) == [occurrence]
