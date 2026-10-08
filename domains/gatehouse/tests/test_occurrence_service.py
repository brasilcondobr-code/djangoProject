from datetime import datetime, timedelta

import pytest
from django.utils import timezone
from django.utils.timezone import make_aware

from domains.gatehouse.exceptions import OccurrenceError
from domains.gatehouse.models import Occurrence
from domains.gatehouse.services import OccurrenceService

pytestmark = pytest.mark.django_db


class TestOccurrenceServiceCreate:

    def test_create_without_date_uses_server_now_minute(
        self, unit, admin_user
    ):
        occurrence = OccurrenceService.create_occurrence(
            {"unit": unit, "subject": "Sem data informada"}, user=admin_user
        )
        diff = abs(occurrence.releaseDate - timezone.now())
        assert diff < timedelta(seconds=60)
        assert occurrence.releaseDate.second == 0
        assert occurrence.releaseDate.microsecond == 0
        assert occurrence.created_user == admin_user
        assert occurrence.is_active is True

    def test_create_without_user_keeps_audit_none(self, unit):
        occurrence = OccurrenceService.create_occurrence(
            {"subject": "Sem usuário"}
        )
        assert occurrence.created_user is None
        assert occurrence.unit is None

    def test_create_with_explicit_datetime(self, unit):
        moment = make_aware(datetime(2026, 10, 5, 14, 30))
        occurrence = OccurrenceService.create_occurrence(
            {"unit": unit, "subject": "Data explícita", "releaseDate": moment}
        )
        assert occurrence.releaseDate == moment

    def test_create_accepts_unit_pk(self, unit):
        occurrence = OccurrenceService.create_occurrence(
            {"unit": unit.pk, "subject": "Por pk"}
        )
        assert occurrence.unit == unit

    def test_create_unknown_unit_pk_raises(self):
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.create_occurrence(
                {"unit": 999999, "subject": "X"}
            )
        assert "Unidade não encontrada" in str(exc.value)

    def test_create_missing_subject_raises(self, unit):
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.create_occurrence({"unit": unit})
        assert "subject" in str(exc.value)

    def test_create_subject_is_stripped(self, unit):
        occurrence = OccurrenceService.create_occurrence(
            {"unit": unit, "subject": "   Assunto limpo   "}
        )
        assert occurrence.subject == "Assunto limpo"

    def test_create_subject_too_long_raises(self, unit):
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.create_occurrence(
                {"unit": unit, "subject": "x" * 256}
            )
        assert "no máximo 255" in str(exc.value)

    def test_create_invalid_date_type_raises(self, unit):
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.create_occurrence(
                {"unit": unit, "subject": "X", "releaseDate": "não-é-data"}
            )
        assert "Data/hora da ocorrência inválida" in str(exc.value)

    def test_create_with_participants(self, unit, participant_a, participant_b):
        occurrence = OccurrenceService.create_occurrence(
            {"unit": unit, "subject": "Com participantes"},
            participants=[participant_a.pk, participant_b.pk],
        )
        names = set(occurrence.participants.values_list("name", flat=True))
        assert names == {"Participante A", "Participante B"}

    def test_create_participant_other_condominium_raises(
        self, unit, foreign_participant
    ):
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.create_occurrence(
                {"unit": unit, "subject": "Com estranho"},
                participants=[foreign_participant],
            )
        assert "devem pertencer" in str(exc.value)
        assert Occurrence.objects.count() == 0

    def test_create_participant_other_condominium_ok_without_unit(
        self, foreign_participant
    ):
        occurrence = OccurrenceService.create_occurrence(
            {"subject": "Sem unidade"},
            participants=[foreign_participant],
        )
        assert occurrence.participants.count() == 1

    def test_create_unknown_participant_pk_raises(self, unit):
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.create_occurrence(
                {"unit": unit, "subject": "X"}, participants=[999999]
            )
        assert "Colaborador não encontrado" in str(exc.value)

    def test_create_duplicate_raises(self, unit):
        moment = make_aware(datetime(2026, 10, 5, 8, 0))
        OccurrenceService.create_occurrence(
            {"unit": unit, "subject": "Repetida", "releaseDate": moment}
        )
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.create_occurrence(
                {"unit": unit, "subject": "Repetida", "releaseDate": moment}
            )
        assert "Já existe uma ocorrência" in str(exc.value)
        assert Occurrence.objects.count() == 1

    def test_create_null_unit_allows_same_date_and_subject(self):
        """Decisão: NULLs são distintos — duplicidade só com os 3 presentes."""
        moment = make_aware(datetime(2026, 10, 5, 8, 0))
        OccurrenceService.create_occurrence(
            {"subject": "Sem unidade", "releaseDate": moment}
        )
        OccurrenceService.create_occurrence(
            {"subject": "Sem unidade", "releaseDate": moment}
        )
        assert Occurrence.objects.count() == 2


class TestOccurrenceServiceUpdate:

    @pytest.fixture
    def occurrence(self, unit):
        return Occurrence.objects.create(
            unit=unit,
            releaseDate=make_aware(datetime(2026, 10, 5, 10, 0)),
            subject="Original",
            description="Descrição original",
        )

    def test_update_changes_fields(self, occurrence, other_unit, admin_user):
        new_moment = make_aware(datetime(2026, 10, 6, 11, 0))
        updated = OccurrenceService.update_occurrence(
            occurrence,
            {
                "unit": other_unit,
                "releaseDate": new_moment,
                "subject": "Atualizada",
                "description": "Nova descrição",
                "is_active": False,
            },
            user=admin_user,
        )
        updated.refresh_from_db()
        assert updated.unit == other_unit
        assert updated.releaseDate == new_moment
        assert updated.subject == "Atualizada"
        assert updated.description == "Nova descrição"
        assert updated.is_active is False

    def test_update_sets_created_user_to_editor(
        self, occurrence, admin_user, django_user_model
    ):
        creator = django_user_model.objects.create_user(
            username="criador07", email="criador07@teste.com", password="x"
        )
        occurrence.created_user = creator
        occurrence.save()
        updated = OccurrenceService.update_occurrence(
            occurrence, {"description": "Editado"}, user=admin_user
        )
        updated.refresh_from_db()
        assert updated.created_user == admin_user
        assert updated.created_user != creator

    def test_update_without_user_keeps_created_user(
        self, occurrence, admin_user
    ):
        occurrence.created_user = admin_user
        occurrence.save()
        updated = OccurrenceService.update_occurrence(
            occurrence, {"description": "Sem usuário"}
        )
        updated.refresh_from_db()
        assert updated.created_user == admin_user

    def test_update_partial_keeps_missing_fields(self, occurrence):
        updated = OccurrenceService.update_occurrence(
            occurrence, {"description": "Parcial"}
        )
        updated.refresh_from_db()
        assert updated.unit == occurrence.unit
        assert updated.releaseDate == occurrence.releaseDate
        assert updated.subject == occurrence.subject
        assert updated.description == "Parcial"

    def test_update_none_instance_raises(self):
        with pytest.raises(OccurrenceError):
            OccurrenceService.update_occurrence(None, {"subject": "x"})

    def test_update_without_release_date_raises(self, occurrence):
        Occurrence.objects.filter(pk=occurrence.pk).update(releaseDate=None)
        occurrence.refresh_from_db()
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.update_occurrence(occurrence, {})
        assert "releaseDate" in str(exc.value)

    def test_update_duplicate_on_other_record_raises(self, occurrence, unit):
        moment = make_aware(datetime(2026, 11, 1, 9, 0))
        Occurrence.objects.create(
            unit=unit, releaseDate=moment, subject="Conflito"
        )
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.update_occurrence(
                occurrence,
                {"releaseDate": moment, "subject": "Conflito"},
            )
        assert "Já existe uma ocorrência" in str(exc.value)

    def test_update_same_triple_on_self_not_flagged(self, occurrence):
        updated = OccurrenceService.update_occurrence(
            occurrence,
            {
                "releaseDate": occurrence.releaseDate,
                "subject": occurrence.subject,
                "description": "Mesma tripla",
            },
        )
        assert updated.pk == occurrence.pk
        assert updated.description == "Mesma tripla"

    def test_update_participants_replace(
        self, occurrence, participant_a, participant_b
    ):
        occurrence.participants.set([participant_a, participant_b])
        updated = OccurrenceService.update_occurrence(
            occurrence, {}, participants=[participant_a.pk]
        )
        assert updated.participants.count() == 1
        assert participant_a in updated.participants.all()

    def test_update_participants_none_keeps_current(
        self, occurrence, participant_a
    ):
        occurrence.participants.set([participant_a])
        updated = OccurrenceService.update_occurrence(
            occurrence, {"description": "mantém"}
        )
        assert updated.participants.count() == 1

    def test_update_participants_empty_clears(
        self, occurrence, participant_a
    ):
        occurrence.participants.set([participant_a])
        updated = OccurrenceService.update_occurrence(
            occurrence, {}, participants=[]
        )
        assert updated.participants.count() == 0

    def test_update_participants_restriction_raises(
        self, occurrence, foreign_participant
    ):
        with pytest.raises(OccurrenceError) as exc:
            OccurrenceService.update_occurrence(
                occurrence, {}, participants=[foreign_participant]
            )
        assert "devem pertencer" in str(exc.value)
        occurrence.refresh_from_db()
        assert occurrence.participants.count() == 0


class TestOccurrenceServiceDeleteAndQueries:

    def test_delete_removes_record(self, unit):
        occurrence = OccurrenceService.create_occurrence(
            {"unit": unit, "subject": "Apagar"}
        )
        OccurrenceService.delete_occurrence(occurrence)
        assert not Occurrence.objects.filter(pk=occurrence.pk).exists()

    def test_delete_none_raises(self):
        with pytest.raises(OccurrenceError):
            OccurrenceService.delete_occurrence(None)

    def test_get_all_returns_records(self, unit, other_unit):
        OccurrenceService.create_occurrence(
            {
                "unit": unit,
                "subject": "Primeira",
                "releaseDate": make_aware(datetime(2026, 10, 5, 8, 0)),
            }
        )
        OccurrenceService.create_occurrence(
            {
                "unit": other_unit,
                "subject": "Segunda",
                "releaseDate": make_aware(datetime(2026, 10, 6, 8, 0)),
            }
        )
        rows = list(OccurrenceService.get_all_occurrences())
        assert len(rows) == 2
        assert rows[0].releaseDate >= rows[1].releaseDate

    def test_get_all_empty(self):
        assert list(OccurrenceService.get_all_occurrences()) == []
