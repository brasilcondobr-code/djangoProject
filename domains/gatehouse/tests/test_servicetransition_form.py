from datetime import date

import pytest
from django import forms as django_forms

from domains.gatehouse.forms import ServiceTransitionForm, ServiceTransitionObjectForm
from domains.gatehouse.models import ServiceTransition

pytestmark = pytest.mark.django_db


class TestServiceTransitionForm:

    def _valid_data(self, condominium, collaborator_out, collaborator_in):
        return {
            "condominium": condominium.pk,
            "collaboratorEnd": collaborator_out.pk,
            "collaboratorStart": collaborator_in.pk,
            "releaseDate": "2026-09-24",
            "observations": "Passagem realizada",
        }

    def test_form_valid(self, condominium, collaborator_out, collaborator_in):
        form = ServiceTransitionForm(
            data=self._valid_data(condominium, collaborator_out, collaborator_in)
        )
        assert form.is_valid()
        assert form.errors == {}

    def test_required_fields(self, condominium, collaborator_out, collaborator_in):
        for field in ("condominium", "collaboratorEnd", "collaboratorStart", "releaseDate"):
            data = self._valid_data(condominium, collaborator_out, collaborator_in)
            del data[field]
            form = ServiceTransitionForm(data=data)
            assert not form.is_valid()
            assert field in form.errors

    def test_observations_optional(self, condominium, collaborator_out, collaborator_in):
        data = self._valid_data(condominium, collaborator_out, collaborator_in)
        data["observations"] = ""
        form = ServiceTransitionForm(data=data)
        assert form.is_valid()

    def test_release_date_invalid(self, condominium, collaborator_out, collaborator_in):
        data = self._valid_data(condominium, collaborator_out, collaborator_in)
        data["releaseDate"] = "nao-e-data"
        form = ServiceTransitionForm(data=data)
        assert not form.is_valid()
        assert "releaseDate" in form.errors

    def test_widgets_are_plain_select_with_contrast_style(self, condominium, collaborator_out, collaborator_in):
        form = ServiceTransitionForm(
            data=self._valid_data(condominium, collaborator_out, collaborator_in)
        )
        for field_name in ("condominium", "collaboratorEnd", "collaboratorStart"):
            widget = form.fields[field_name].widget
            assert isinstance(widget, django_forms.Select)
            style = widget.attrs.get("style", "")
            assert "color: #212529" in style
            assert "background-color: #ffffff" in style

    def test_date_widget_uses_html5_date_input(self, condominium, collaborator_out, collaborator_in):
        form = ServiceTransitionForm(
            data=self._valid_data(condominium, collaborator_out, collaborator_in)
        )
        assert form.fields["releaseDate"].widget.input_type == "date"

    def test_queryset_excludes_inactive_condominium(self, condominium, inactive_condominium, collaborator_out, collaborator_in):
        form = ServiceTransitionForm(
            data=self._valid_data(condominium, collaborator_out, collaborator_in)
        )
        pks = list(form.fields["condominium"].queryset.values_list("pk", flat=True))
        assert condominium.pk in pks
        assert inactive_condominium.pk not in pks

    def test_queryset_preserves_selected_inactive_on_edit(self, inactive_condominium, collaborator_out, collaborator_in):
        transition = ServiceTransition.objects.create(
            condominium=inactive_condominium,
            collaboratorEnd=collaborator_out,
            collaboratorStart=collaborator_in,
            releaseDate=date(2026, 9, 24),
        )
        form = ServiceTransitionForm(instance=transition)
        pks = list(form.fields["condominium"].queryset.values_list("pk", flat=True))
        assert inactive_condominium.pk in pks

    def test_queryset_excludes_inactive_collaborator(self, condominium, collaborator_out, collaborator_in, collaborator_factory):
        inactive = collaborator_factory("Inativo", is_active=False)
        form = ServiceTransitionForm(
            data=self._valid_data(condominium, collaborator_out, collaborator_in)
        )
        pks = list(form.fields["collaboratorEnd"].queryset.values_list("pk", flat=True))
        assert collaborator_out.pk in pks
        assert inactive.pk not in pks

    def test_queryset_ordered_by_name(self, condominium, collaborator_out, collaborator_in, collaborator_factory):
        collaborator_factory("Aaa Colaborador")
        form = ServiceTransitionForm(
            data=self._valid_data(condominium, collaborator_out, collaborator_in)
        )
        names = list(form.fields["collaboratorEnd"].queryset.values_list("name", flat=True))
        assert names == sorted(names)

    def test_can_save_without_observations(self, condominium, collaborator_out, collaborator_in):
        data = self._valid_data(condominium, collaborator_out, collaborator_in)
        data["observations"] = "   "
        form = ServiceTransitionForm(data=data)
        assert form.is_valid()
        assert form.cleaned_data["observations"] in ("", None)


class TestServiceTransitionObjectForm:

    def _valid_data(self, category):
        return {
            "categoryObj": category.pk,
            "itemObj": "Monitor",
            "amountObj": 2,
            "shiftDate": "2026-09-24",
        }

    def test_form_valid(self, category):
        form = ServiceTransitionObjectForm(data=self._valid_data(category))
        assert form.is_valid()
        assert form.errors == {}

    def test_item_required(self, category):
        data = self._valid_data(category)
        del data["itemObj"]
        form = ServiceTransitionObjectForm(data=data)
        assert not form.is_valid()
        assert "itemObj" in form.errors

    def test_item_blank_spaces_rejected(self, category):
        data = self._valid_data(category)
        data["itemObj"] = "   "
        form = ServiceTransitionObjectForm(data=data)
        assert not form.is_valid()
        assert "itemObj" in form.errors

    def test_item_stripped(self, category):
        data = self._valid_data(category)
        data["itemObj"] = "   Monitor   "
        form = ServiceTransitionObjectForm(data=data)
        assert form.is_valid()
        assert form.cleaned_data["itemObj"] == "Monitor"

    @pytest.mark.parametrize("amount", [0, -1, "1.5"])
    def test_amount_rejected_values(self, category, amount):
        data = self._valid_data(category)
        data["amountObj"] = amount
        form = ServiceTransitionObjectForm(data=data)
        assert not form.is_valid()
        assert "amountObj" in form.errors

    def test_amount_minimum_one_accepted(self, category):
        data = self._valid_data(category)
        data["amountObj"] = 1
        form = ServiceTransitionObjectForm(data=data)
        assert form.is_valid()

    def test_shift_date_required(self, category):
        data = self._valid_data(category)
        del data["shiftDate"]
        form = ServiceTransitionObjectForm(data=data)
        assert not form.is_valid()
        assert "shiftDate" in form.errors

    def test_time_fields_not_in_form(self):
        form = ServiceTransitionObjectForm()
        for field_name in ("startTime", "endTime"):
            assert field_name not in form.fields

    def test_shift_date_defaults_to_today(self):
        import re

        from django.utils import timezone

        form = ServiceTransitionObjectForm()
        html = str(form["shiftDate"])
        match = re.search(r'<input type="date" name="shiftDate"[^>]*value="([^"]*)"', html)
        assert match is not None, "input visivel type=date nao encontrado"
        assert match.group(1) == timezone.localdate().isoformat()
        assert match.group(1) != "26/09/2026"

    def test_date_widget_uses_html5_date_input(self, category):
        form = ServiceTransitionObjectForm(data=self._valid_data(category))
        assert form.fields["shiftDate"].widget.input_type == "date"

    def test_category_widget_is_plain_select(self, category):
        form = ServiceTransitionObjectForm(data=self._valid_data(category))
        widget = form.fields["categoryObj"].widget
        assert isinstance(widget, django_forms.Select)
        assert "background-color: #ffffff" in widget.attrs.get("style", "")

    def test_category_queryset_excludes_inactive(self, category, inactive_category):
        form = ServiceTransitionObjectForm(data=self._valid_data(category))
        pks = list(form.fields["categoryObj"].queryset.values_list("pk", flat=True))
        assert category.pk in pks
        assert inactive_category.pk not in pks

    def test_description_not_in_form(self):
        form = ServiceTransitionObjectForm()
        assert "description" not in form.fields



class TestISODateInput:

    def test_formats_date_as_iso(self):
        from datetime import date

        from domains.gatehouse.forms import ISODateInput

        assert ISODateInput().format_value(date(2026, 9, 24)) == "2026-09-24"

    def test_passes_through_iso_string(self):
        from domains.gatehouse.forms import ISODateInput

        assert ISODateInput().format_value("2026-09-24") == "2026-09-24"

    def test_none_and_empty_return_none(self):
        from domains.gatehouse.forms import ISODateInput

        assert ISODateInput().format_value(None) is None
        assert ISODateInput().format_value("") is None

    def test_main_form_renders_release_date_as_iso(self):
        import re
        from datetime import date

        from domains.gatehouse.forms import ServiceTransitionForm
        from domains.gatehouse.models import ServiceTransition

        instance = ServiceTransition(releaseDate=date(2026, 9, 24))
        form = ServiceTransitionForm(instance=instance)
        html = str(form["releaseDate"])
        match = re.search(r'<input type="date" name="releaseDate"[^>]*value="([^"]*)"', html)
        assert match is not None
        assert match.group(1) == "2026-09-24"
