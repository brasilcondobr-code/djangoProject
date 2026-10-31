from datetime import date

import pytest

from domains.reservations.forms import MoveReservationsForm
from domains.reservations.models import MoveReservations


@pytest.mark.django_db
class TestMoveReservationsForm:

    def _data(self, unit, **overrides):
        data = {
            "condominium": unit.pk,
            "typeOfChange": "E",
            "startDate": "2026-11-10",
            "endDate": "2026-11-12",
            "applicant": "Maria Souza",
            "observations": "Observação",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_form_valid_entrada(self, unit):
        form = MoveReservationsForm(data=self._data(unit))
        assert form.is_valid(), form.errors
        assert form.cleaned_data["typeOfChange"] == "E"

    def test_form_valid_saida(self, unit):
        form = MoveReservationsForm(
            data=self._data(unit, typeOfChange="S")
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["typeOfChange"] == "S"

    def test_condominium_required(self, unit):
        data = self._data(unit)
        data.pop("condominium")
        form = MoveReservationsForm(data=data)
        assert not form.is_valid()
        assert "condominium" in form.errors
        assert "Selecione a unidade da mudança." in str(
            form.errors["condominium"]
        )

    def test_type_of_change_required(self, unit):
        form = MoveReservationsForm(
            data=self._data(unit, typeOfChange="")
        )
        assert not form.is_valid()
        assert "typeOfChange" in form.errors
        assert "Selecione o tipo de mudança." in str(
            form.errors["typeOfChange"]
        )

    def test_type_of_change_invalid_choice(self, unit):
        form = MoveReservationsForm(
            data=self._data(unit, typeOfChange="X")
        )
        assert not form.is_valid()
        assert "typeOfChange" in form.errors

    def test_start_date_required(self, unit):
        data = self._data(unit)
        data.pop("startDate")
        form = MoveReservationsForm(data=data)
        assert not form.is_valid()
        assert "startDate" in form.errors
        assert "Informe a data inicial." in str(form.errors["startDate"])

    def test_end_date_required(self, unit):
        data = self._data(unit)
        data.pop("endDate")
        form = MoveReservationsForm(data=data)
        assert not form.is_valid()
        assert "endDate" in form.errors
        assert "Informe a data final." in str(form.errors["endDate"])

    def test_applicant_required(self, unit):
        form = MoveReservationsForm(
            data=self._data(unit, applicant="")
        )
        assert not form.is_valid()
        assert "applicant" in form.errors
        assert "Informe o solicitante." in str(form.errors["applicant"])

    def test_applicant_only_spaces(self, unit):
        form = MoveReservationsForm(
            data=self._data(unit, applicant="   ")
        )
        assert not form.is_valid()
        assert "applicant" in form.errors

    def test_applicant_max_length(self, unit):
        form = MoveReservationsForm(
            data=self._data(unit, applicant="x" * 256)
        )
        assert not form.is_valid()
        assert "applicant" in form.errors

    def test_applicant_is_stripped(self, unit):
        form = MoveReservationsForm(
            data=self._data(unit, applicant="  Maria Souza  ")
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["applicant"] == "Maria Souza"

    def test_end_date_before_start_date_rejected(self, unit):
        form = MoveReservationsForm(
            data=self._data(
                unit,
                startDate="2026-11-15",
                endDate="2026-11-10",
            )
        )
        assert not form.is_valid()
        assert "endDate" in form.errors
        assert "A data final deve ser maior ou igual à data inicial." in str(
            form.errors["endDate"]
        )

    def test_end_date_equal_start_date_allowed(self, unit):
        form = MoveReservationsForm(
            data=self._data(
                unit,
                startDate="2026-11-10",
                endDate="2026-11-10",
            )
        )
        assert form.is_valid(), form.errors

    def test_observations_optional(self, unit):
        data = self._data(unit)
        data.pop("observations")
        form = MoveReservationsForm(data=data)
        assert form.is_valid(), form.errors
        assert form.cleaned_data["observations"] == ""

    def test_is_active_default_initial(self):
        form = MoveReservationsForm()
        assert form.fields["is_active"].initial is True

    def test_status_and_audit_not_exposed(self):
        form = MoveReservationsForm()
        for name in (
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ):
            assert name not in form.fields

    def test_widgets_labels_and_help_texts(self):
        form = MoveReservationsForm()

        applicant = form.fields["applicant"].widget
        assert applicant.attrs["class"] == "form-control"
        assert applicant.attrs["placeholder"] == "Nome do solicitante"
        assert applicant.attrs["maxlength"] == "255"

        observations = form.fields["observations"].widget
        assert observations.attrs["rows"] == 3
        assert observations.attrs["placeholder"] == "Observações (opcional)"

        assert form.fields["startDate"].widget.input_type == "date"
        assert form.fields["endDate"].widget.input_type == "date"

        assert form.fields["typeOfChange"].widget.__class__.__name__ == (
            "Select"
        )
        assert form.fields["typeOfChange"].widget.attrs["class"] == (
            "form-control"
        )
        assert form.fields["condominium"].label == "Unidade"
        assert form.fields["typeOfChange"].label == "Tipo de mudança"
        assert form.fields["startDate"].label == "Data inicial"
        assert form.fields["endDate"].label == "Data final"
        assert form.fields["applicant"].label == "Solicitante"
        assert form.fields["observations"].label == "Observações"
        assert form.fields["is_active"].label == "Ativo"

        assert "unidade" in form.fields["condominium"].help_text.lower()
        assert "entrada" in form.fields["typeOfChange"].help_text.lower()

    def test_iso_date_widget_formats_value(self):
        assert (
            MoveReservationsForm()
            .fields["startDate"]
            .widget.format_value(date(2026, 11, 10))
            == "2026-11-10"
        )

    def test_edit_blocked_in_execution(self, unit):
        move = MoveReservations.objects.create(
            condominium=unit,
            typeOfChange="E",
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 12),
            applicant="Maria Souza",
            status=MoveReservations.Status.EXECUCAO,
        )
        form = MoveReservationsForm(
            instance=move, data=self._data(unit)
        )
        assert not form.is_valid()
        assert "Somente mudanças em Agendamento podem ser editadas." in str(
            form.non_field_errors()
        )

    def test_edit_blocked_in_finalized(self, unit):
        move = MoveReservations.objects.create(
            condominium=unit,
            typeOfChange="S",
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 12),
            applicant="Maria Souza",
            status=MoveReservations.Status.FINALIZADO,
        )
        form = MoveReservationsForm(
            instance=move, data=self._data(unit)
        )
        assert not form.is_valid()
        assert "Somente mudanças em Agendamento podem ser editadas." in str(
            form.non_field_errors()
        )

    def test_edit_allowed_in_agendamento(self, unit):
        move = MoveReservations.objects.create(
            condominium=unit,
            typeOfChange="E",
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 12),
            applicant="Maria Souza",
        )
        form = MoveReservationsForm(
            instance=move,
            data=self._data(unit, applicant="Maria Alterada"),
        )
        assert form.is_valid(), form.errors
