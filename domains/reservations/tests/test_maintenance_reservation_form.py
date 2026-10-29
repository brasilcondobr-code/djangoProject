from datetime import date

import pytest

from domains.parameters.models import TypesOfMaintenanceReservations
from domains.reservations.forms import MaintenanceReservationsForm
from domains.reservations.models import MaintenanceReservations


@pytest.mark.django_db
class TestMaintenanceReservationsForm:

    def _data(self, unit, maintenance_type, **overrides):
        data = {
            "condominium": unit.pk,
            "typesOfMaintenance": maintenance_type.pk,
            "startDate": "2026-11-10",
            "endDate": "2026-11-12",
            "applicant": "Maria Souza",
            "observations": "Observação",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_form_valid(self, unit, maintenance_type):
        form = MaintenanceReservationsForm(
            data=self._data(unit, maintenance_type)
        )
        assert form.is_valid(), form.errors

    def test_condominium_required(self, unit, maintenance_type):
        data = self._data(unit, maintenance_type)
        data.pop("condominium")
        form = MaintenanceReservationsForm(data=data)
        assert not form.is_valid()
        assert "condominium" in form.errors
        assert "Selecione a unidade da manutenção." in str(
            form.errors["condominium"]
        )

    def test_types_of_maintenance_required(self, unit, maintenance_type):
        data = self._data(unit, maintenance_type)
        data.pop("typesOfMaintenance")
        form = MaintenanceReservationsForm(data=data)
        assert not form.is_valid()
        assert "typesOfMaintenance" in form.errors
        assert "Selecione o tipo de manutenção." in str(
            form.errors["typesOfMaintenance"]
        )

    def test_start_date_required(self, unit, maintenance_type):
        data = self._data(unit, maintenance_type)
        data.pop("startDate")
        form = MaintenanceReservationsForm(data=data)
        assert not form.is_valid()
        assert "startDate" in form.errors
        assert "Informe a data inicial." in str(form.errors["startDate"])

    def test_end_date_required(self, unit, maintenance_type):
        data = self._data(unit, maintenance_type)
        data.pop("endDate")
        form = MaintenanceReservationsForm(data=data)
        assert not form.is_valid()
        assert "endDate" in form.errors
        assert "Informe a data final." in str(form.errors["endDate"])

    def test_applicant_required(self, unit, maintenance_type):
        form = MaintenanceReservationsForm(
            data=self._data(unit, maintenance_type, applicant="")
        )
        assert not form.is_valid()
        assert "applicant" in form.errors
        assert "Informe o solicitante." in str(form.errors["applicant"])

    def test_applicant_only_spaces(self, unit, maintenance_type):
        form = MaintenanceReservationsForm(
            data=self._data(unit, maintenance_type, applicant="   ")
        )
        assert not form.is_valid()
        assert "applicant" in form.errors

    def test_applicant_max_length(self, unit, maintenance_type):
        form = MaintenanceReservationsForm(
            data=self._data(unit, maintenance_type, applicant="x" * 256)
        )
        assert not form.is_valid()
        assert "applicant" in form.errors

    def test_applicant_is_stripped(self, unit, maintenance_type):
        form = MaintenanceReservationsForm(
            data=self._data(
                unit, maintenance_type, applicant="  Maria Souza  "
            )
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["applicant"] == "Maria Souza"

    def test_end_date_before_start_date_rejected(
        self, unit, maintenance_type
    ):
        form = MaintenanceReservationsForm(
            data=self._data(
                unit,
                maintenance_type,
                startDate="2026-11-15",
                endDate="2026-11-10",
            )
        )
        assert not form.is_valid()
        assert "endDate" in form.errors
        assert "A data final deve ser maior ou igual à data inicial." in str(
            form.errors["endDate"]
        )

    def test_end_date_equal_start_date_allowed(self, unit, maintenance_type):
        form = MaintenanceReservationsForm(
            data=self._data(
                unit,
                maintenance_type,
                startDate="2026-11-10",
                endDate="2026-11-10",
            )
        )
        assert form.is_valid(), form.errors

    def test_observations_optional(self, unit, maintenance_type):
        data = self._data(unit, maintenance_type)
        data.pop("observations")
        form = MaintenanceReservationsForm(data=data)
        assert form.is_valid(), form.errors
        assert form.cleaned_data["observations"] == ""

    def test_is_active_default_initial(self):
        form = MaintenanceReservationsForm()
        assert form.fields["is_active"].initial is True

    def test_status_and_audit_not_exposed(self):
        form = MaintenanceReservationsForm()
        for name in (
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ):
            assert name not in form.fields

    def test_widgets_labels_and_help_texts(self):
        form = MaintenanceReservationsForm()

        applicant = form.fields["applicant"].widget
        assert applicant.attrs["class"] == "form-control"
        assert applicant.attrs["placeholder"] == "Nome do solicitante"
        assert applicant.attrs["maxlength"] == "255"

        observations = form.fields["observations"].widget
        assert observations.attrs["rows"] == 3
        assert observations.attrs["placeholder"] == "Observações (opcional)"

        start = form.fields["startDate"].widget
        end = form.fields["endDate"].widget
        assert start.input_type == "date"
        assert end.input_type == "date"

        assert form.fields["condominium"].label == "Unidade"
        assert form.fields["typesOfMaintenance"].label == "Tipo de manutenção"
        assert form.fields["startDate"].label == "Data inicial"
        assert form.fields["endDate"].label == "Data final"
        assert form.fields["applicant"].label == "Solicitante"
        assert form.fields["observations"].label == "Observações"
        assert form.fields["is_active"].label == "Ativo"

        assert "unidade" in form.fields["condominium"].help_text.lower()
        assert "tipo" in form.fields["typesOfMaintenance"].help_text.lower()

    def test_iso_date_widget_formats_value(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            condominium=unit,
            typesOfMaintenance=maintenance_type,
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 12),
            applicant="Maria Souza",
        )
        form = MaintenanceReservationsForm(instance=maintenance)
        assert (
            form.fields["startDate"].widget.format_value(date(2026, 11, 10))
            == "2026-11-10"
        )
        assert (
            form.fields["endDate"].widget.format_value(date(2026, 11, 12))
            == "2026-11-12"
        )

    def test_inactive_type_not_available_for_new_records(self, unit):
        inactive = TypesOfMaintenanceReservations.objects.create(
            description="Manutenção Inativa",
            is_active=False,
        )
        form = MaintenanceReservationsForm()
        assert inactive not in form.fields["typesOfMaintenance"].queryset

    def test_current_inactive_type_kept_on_edit(self, unit):
        maintenance_type = TypesOfMaintenanceReservations.objects.create(
            description="Manutenção Desativada",
            is_active=True,
        )
        maintenance = MaintenanceReservations.objects.create(
            condominium=unit,
            typesOfMaintenance=maintenance_type,
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 12),
            applicant="Maria Souza",
        )
        TypesOfMaintenanceReservations.objects.filter(
            pk=maintenance_type.pk
        ).update(is_active=False)

        form = MaintenanceReservationsForm(instance=maintenance)
        assert maintenance_type in form.fields["typesOfMaintenance"].queryset

    def test_edit_blocked_in_execution(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            condominium=unit,
            typesOfMaintenance=maintenance_type,
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 12),
            applicant="Maria Souza",
            status=MaintenanceReservations.Status.EXECUCAO,
        )
        form = MaintenanceReservationsForm(
            instance=maintenance,
            data=self._data(unit, maintenance_type),
        )
        assert not form.is_valid()
        assert "Somente manutenções em Agendamento podem ser editadas." in str(
            form.non_field_errors()
        )

    def test_edit_blocked_in_finalized(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            condominium=unit,
            typesOfMaintenance=maintenance_type,
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 12),
            applicant="Maria Souza",
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        form = MaintenanceReservationsForm(
            instance=maintenance,
            data=self._data(unit, maintenance_type),
        )
        assert not form.is_valid()
        assert "Somente manutenções em Agendamento podem ser editadas." in str(
            form.non_field_errors()
        )

    def test_edit_allowed_in_agendamento(self, unit, maintenance_type):
        maintenance = MaintenanceReservations.objects.create(
            condominium=unit,
            typesOfMaintenance=maintenance_type,
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 12),
            applicant="Maria Souza",
        )
        form = MaintenanceReservationsForm(
            instance=maintenance,
            data=self._data(
                unit, maintenance_type, applicant="Maria Alterada"
            ),
        )
        assert form.is_valid(), form.errors
