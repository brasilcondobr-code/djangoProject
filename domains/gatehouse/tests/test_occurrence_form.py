from datetime import timedelta

import pytest
from django.utils import timezone

from domains.gatehouse.forms import OccurrenceForm
from domains.gatehouse.models import Occurrence
from domains.gatehouse.services import OccurrenceService

pytestmark = pytest.mark.django_db


def _data(**overrides):
    data = {
        "subject": "Ocorrência de teste",
        "is_active": "on",
    }
    data.update(overrides)
    return data


def _form(unit=None, participants=None, **overrides):
    data = _data(**overrides)
    if unit is not None:
        data["unit"] = str(unit.pk)
    files = {}
    if participants is not None:
        data["participants"] = [str(p.pk) for p in participants]
    return OccurrenceForm(data=data)


class TestOccurrenceForm:

    def test_create_valid_without_release_date_fills_now(self, unit):
        form = _form(unit)
        assert form.is_valid(), form.errors
        cleaned = form.cleaned_data["releaseDate"]
        diff = abs(cleaned - timezone.now())
        assert diff < timedelta(seconds=60)
        assert cleaned.second == 0
        assert cleaned.microsecond == 0

    def test_create_ignores_client_sent_datetime(self, unit):
        form = _form(unit, releaseDate="2020-01-01T10:00")
        assert form.is_valid(), form.errors
        cleaned = form.cleaned_data["releaseDate"]
        diff = abs(cleaned - timezone.now())
        assert diff < timedelta(seconds=60)

    def test_create_widget_readonly_and_initial(self):
        form = OccurrenceForm()
        field = form.fields["releaseDate"]
        assert field.widget.attrs.get("readonly") == "readonly"
        # Input.__init__ move attrs["type"] para input_type do widget
        assert field.widget.input_type == "datetime-local"
        assert field.initial is not None
        assert field.required is False

    def test_edit_widget_editable_and_required(self, unit):
        occurrence = Occurrence.objects.create(
            unit=unit,
            releaseDate=timezone.now(),
            subject="Para editar",
        )
        form = OccurrenceForm(instance=occurrence)
        field = form.fields["releaseDate"]
        assert "readonly" not in field.widget.attrs
        assert field.required is True

    def test_subject_required(self, unit):
        form = _form(unit, subject="")
        assert not form.is_valid()
        assert "subject" in form.errors
        assert "O assunto é obrigatório." in form.errors["subject"]

    def test_subject_max_length(self, unit):
        form = _form(unit, subject="x" * 256)
        assert not form.is_valid()
        assert "subject" in form.errors

    def test_subject_255_chars_ok(self, unit):
        form = _form(unit, subject="y" * 255)
        assert form.is_valid(), form.errors

    def test_unit_optional(self):
        form = _form()
        assert form.is_valid(), form.errors

    def test_description_optional(self, unit):
        form = _form(unit, description="")
        assert form.is_valid(), form.errors

    def test_participants_multiple_saved(self, unit, participant_a, participant_b):
        form = _form(unit, participants=[participant_a, participant_b])
        assert form.is_valid(), form.errors
        occurrence = form.save()
        names = set(occurrence.participants.values_list("name", flat=True))
        assert names == {"Participante A", "Participante B"}

    def test_participant_from_other_condominium_rejected_with_unit(
        self, unit, foreign_participant
    ):
        form = _form(unit, participants=[foreign_participant])
        assert not form.is_valid()
        assert "participants" in form.errors
        assert "devem pertencer" in form.errors["participants"][0]

    def test_participant_from_other_condominium_ok_without_unit(
        self, foreign_participant
    ):
        """Sem unidade selecionada, qualquer colaborador vale (decisão)."""
        form = _form(participants=[foreign_participant])
        assert form.is_valid(), form.errors

    def test_participant_same_condominium_other_unit_ok(
        self, other_unit, participant_a
    ):
        """Outra unidade do MESMO condomínio é aceita."""
        form = _form(other_unit, participants=[participant_a])
        assert form.is_valid(), form.errors

    def test_duplicate_triple_rejected(self, unit):
        Occurrence.objects.create(
            unit=unit,
            releaseDate=OccurrenceService.server_now(),
            subject="Ocorrência de teste",
        )
        form = _form(unit)
        assert not form.is_valid()
        assert "subject" in form.errors
        assert "Já existe uma ocorrência" in form.errors["subject"][0]

    def test_edit_same_record_not_flagged_as_duplicate(self, unit):
        occurrence = Occurrence.objects.create(
            unit=unit,
            releaseDate=OccurrenceService.server_now(),
            subject="Ocorrência de teste",
        )
        form = OccurrenceForm(
            data=_data(
                unit=str(unit.pk),
                releaseDate=timezone.localtime(
                    occurrence.releaseDate
                ).strftime("%Y-%m-%dT%H:%M"),
                description="Editado",
            ),
            instance=occurrence,
        )
        assert form.is_valid(), form.errors

    def test_duplicate_triple_rejected_on_edit(self, unit):
        release = OccurrenceService.server_now()
        Occurrence.objects.create(
            unit=unit, releaseDate=release, subject="Duplicada"
        )
        other = Occurrence.objects.create(
            unit=unit, releaseDate=release, subject="Outro assunto"
        )
        form = OccurrenceForm(
            data=_data(
                unit=str(unit.pk),
                subject="Duplicada",
                releaseDate=timezone.localtime(release).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            ),
            instance=other,
        )
        assert not form.is_valid()
        assert "subject" in form.errors
        assert "Já existe uma ocorrência" in form.errors["subject"][0]

    def test_null_unit_same_date_and_subject_allowed(self):
        """Decisão: duplicidade só com os 3 valores presentes (padrão 04)."""
        Occurrence.objects.create(
            unit=None,
            releaseDate=OccurrenceService.server_now(),
            subject="Ocorrência de teste",
        )
        form = _form()
        assert form.is_valid(), form.errors

    def test_edit_can_change_release_date(self, unit):
        occurrence = Occurrence.objects.create(
            unit=unit,
            releaseDate=timezone.now(),
            subject="Mudar data",
        )
        form = OccurrenceForm(
            data=_data(
                unit=str(unit.pk),
                subject="Mudar data",
                releaseDate="2026-12-24T09:30",
            ),
            instance=occurrence,
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["releaseDate"].strftime("%Y-%m-%d %H:%M") == (
            "2026-12-24 09:30"
        )

    def test_edit_without_release_date_rejected(self, unit):
        occurrence = Occurrence.objects.create(
            unit=unit,
            releaseDate=timezone.now(),
            subject="Exigir data",
        )
        data = _data(unit=str(unit.pk), subject="Exigir data")
        form = OccurrenceForm(data=data, instance=occurrence)
        assert not form.is_valid()
        assert "releaseDate" in form.errors

    def test_participants_queryset_excludes_inactive(
        self, participant_a, collaborator_factory
    ):
        inactive = collaborator_factory("Colaborador Inativo", is_active=False)
        form = OccurrenceForm()
        pks = set(
            form.fields["participants"].queryset.values_list("pk", flat=True)
        )
        assert participant_a.pk in pks
        assert inactive.pk not in pks

    def test_participants_queryset_keeps_selected_inactive_on_edit(
        self, collaborator_factory, unit
    ):
        inactive = collaborator_factory("Colaborador Inativo", is_active=False)
        occurrence = Occurrence.objects.create(
            unit=unit,
            releaseDate=timezone.now(),
            subject="Com inativo",
        )
        occurrence.participants.add(inactive)
        form = OccurrenceForm(instance=occurrence)
        pks = set(
            form.fields["participants"].queryset.values_list("pk", flat=True)
        )
        assert inactive.pk in pks

    def test_save_sets_audit_dates(self, unit):
        form = _form(unit)
        assert form.is_valid(), form.errors
        occurrence = form.save()
        assert occurrence.created_at is not None
        assert occurrence.updated_at is not None
