from datetime import date
from decimal import Decimal

import pytest
from django import forms as django_forms

from domains.financial.forms import NewReleaseForm
from domains.financial.models import NewRelease


@pytest.mark.django_db
class TestNewReleaseForm:

    def test_valid_form_signs_value_and_normalizes_scope(
        self, _valid_form_data
    ):
        form = NewReleaseForm(data=_valid_form_data)

        assert form.is_valid(), form.errors
        assert form.cleaned_data["scope"] == date(2026, 1, 1)
        assert form.cleaned_data["value"] == Decimal("-150.00")

        instance = form.save(commit=False)
        assert instance.scope == date(2026, 1, 1)
        assert instance.value == Decimal("-150.00")

    def test_credit_value_is_positive(self, _valid_form_data):
        data = dict(_valid_form_data)
        data["launchType"] = NewRelease.LaunchType.CREDITO

        form = NewReleaseForm(data=data)

        assert form.is_valid(), form.errors
        assert form.cleaned_data["value"] == Decimal("150.00")

    def test_empty_value_is_none(self, _valid_form_data):
        data = dict(_valid_form_data)
        data["value"] = ""

        form = NewReleaseForm(data=data)

        assert form.is_valid(), form.errors
        assert form.cleaned_data["value"] is None

    def test_scope_requires_month_format(self, _valid_form_data):
        data = dict(_valid_form_data)
        data["scope"] = "01/2026"

        form = NewReleaseForm(data=data)

        assert not form.is_valid()
        assert "scope" in form.errors

    @pytest.mark.parametrize(
        "raw_scope",
        ["2026-01", "1-2026", "01-26", "13-2026", "00-2026", ""],
    )
    def test_invalid_scope_formats(self, _valid_form_data, raw_scope):
        data = dict(_valid_form_data)
        data["scope"] = raw_scope

        form = NewReleaseForm(data=data)

        assert not form.is_valid()
        assert "scope" in form.errors

    def test_required_fields(self, _valid_form_data):
        data = {key: "" for key in _valid_form_data}
        data["launchType"] = ""

        form = NewReleaseForm(data=data)

        assert not form.is_valid()
        for field in (
            "condominium",
            "paymaster",
            "title",
            "scope",
            "launchDate",
            "chartOfAccounts",
            "fund",
            "launchType",
        ):
            assert field in form.errors

    def test_title_is_trimmed(self, _valid_form_data):
        data = dict(_valid_form_data)
        data["title"] = "  Taxa do mês  "

        form = NewReleaseForm(data=data)

        assert form.is_valid(), form.errors
        assert form.cleaned_data["title"] == "Taxa do mês"

    def test_paymaster_must_belong_to_unit(
        self, _valid_form_data, _resident_two
    ):
        data = dict(_valid_form_data)
        data["paymaster"] = _resident_two.pk

        form = NewReleaseForm(data=data)

        assert not form.is_valid()
        assert "paymaster" in form.errors

    def test_chart_of_account_must_belong_to_unit_condominium(
        self, _valid_form_data, _chart_account_other
    ):
        data = dict(_valid_form_data)
        data["chartOfAccounts"] = _chart_account_other.pk

        form = NewReleaseForm(data=data)

        assert not form.is_valid()
        assert "chartOfAccounts" in form.errors

    def test_fund_must_belong_to_unit_condominium(
        self, _valid_form_data, _fund_other
    ):
        data = dict(_valid_form_data)
        data["fund"] = _fund_other.pk

        form = NewReleaseForm(data=data)

        assert not form.is_valid()
        assert "fund" in form.errors

    @pytest.mark.parametrize("raw_value", ["0,00", "-10,00", "abc"])
    def test_invalid_value(self, _valid_form_data, raw_value):
        data = dict(_valid_form_data)
        data["value"] = raw_value

        form = NewReleaseForm(data=data)

        assert not form.is_valid()
        assert "value" in form.errors

    def test_invalid_launch_type(self, _valid_form_data):
        data = dict(_valid_form_data)
        data["launchType"] = "X"

        form = NewReleaseForm(data=data)

        assert not form.is_valid()
        assert "launchType" in form.errors

    def test_paymaster_queryset_is_filtered_by_unit(
        self,
        _unit,
        _resident,
        _resident_two,
        _resident_inactive,
    ):
        form = NewReleaseForm()

        # Sem unidade selecionada não há pagadores disponíveis.
        assert form.fields["paymaster"].queryset.count() == 0

        bound = NewReleaseForm(data={"condominium": _unit.pk})
        queryset = bound.fields["paymaster"].queryset
        assert _resident in queryset
        assert _resident_two not in queryset
        assert _resident_inactive not in queryset

    def test_paymaster_option_includes_type_and_unit(
        self, _unit, _resident
    ):
        form = NewReleaseForm(data={"condominium": _unit.pk})
        rendered = str(form["paymaster"])

        assert "Morador Um | Morador(a) | Condomínio Teste - A - 101" in (
            rendered
        )

    def test_title_placeholder_defaults_to_scope_format(self):
        form = NewReleaseForm()

        assert form.fields["title"].widget.attrs["placeholder"] == (
            "Taxa condominial de: MM-AAAA"
        )

    def test_widgets(self):
        form = NewReleaseForm()

        assert isinstance(form.fields["scope"].widget, django_forms.TextInput)
        assert form.fields["scope"].widget.input_type == "text"
        assert form.fields["scope"].max_length == 7
        assert form.fields["launchDate"].widget.input_type == "date"
        assert isinstance(
            form.fields["launchType"].widget, django_forms.RadioSelect
        )
        assert "mask-currency" in form.fields["value"].widget.attrs["class"]
        assert "form-check-input" in form.fields[
            "is_active"
        ].widget.attrs["class"]

    def test_widgets_render_expected_formats(self, _new_release):
        form = NewReleaseForm(instance=_new_release)

        assert 'value="01-2026"' in str(form["scope"])
        assert 'value="2026-01-10"' in str(form["launchDate"])

    def test_meta_fields_exclude_server_side_fields(self):
        assert NewReleaseForm.Meta.fields == (
            "condominium",
            "paymaster",
            "launchDate",
            "scope",
            "title",
            "chartOfAccounts",
            "fund",
            "launchType",
            "value",
            "notes",
            "is_active",
        )
        assert "status" not in NewReleaseForm.Meta.fields
        assert "created_by" not in NewReleaseForm.Meta.fields
        assert "updated_by" not in NewReleaseForm.Meta.fields

    def test_new_form_defaults_launch_date_to_today(self):
        from django.utils import timezone

        form = NewReleaseForm()

        assert form.initial["launchDate"] == timezone.localdate()

    def test_new_form_defaults_scope_to_current_month(self):
        from django.utils import timezone

        form = NewReleaseForm()
        expected = timezone.localdate().strftime("%m-%Y")

        assert form.initial["scope"] == expected
        assert f'value="{expected}"' in str(form["scope"])

    def test_new_form_defaults_title_from_scope(self):
        from django.utils import timezone

        form = NewReleaseForm()
        expected_scope = timezone.localdate().strftime("%m-%Y")
        expected_title = f"Taxa condominial de: {expected_scope}"

        assert form.initial["title"] == expected_title
        assert f'value="{expected_title}"' in str(form["title"])

    def test_edit_form_preserves_existing_title(self, _new_release):
        form = NewReleaseForm(instance=_new_release)

        assert form.initial["title"] == _new_release.title

    def test_launch_type_renders_as_radio_group(self):
        form = NewReleaseForm()
        rendered = str(form["launchType"])

        assert 'type="radio"' in rendered
        assert 'name="launchType"' in rendered
        assert not rendered.startswith(
            '<div id="id_launchType" class="form-check-input"'
        )

    def test_paymaster_has_residents_endpoint_attribute(self):
        form = NewReleaseForm()
        rendered = str(form["paymaster"])

        assert "data-residents-url=" in rendered
        assert "residents-by-unit" in rendered

    def test_initial_value_is_absolute_and_formatted(self, _new_release):
        form = NewReleaseForm(instance=_new_release)

        assert form.initial["value"] == "150,00"
        assert form.initial["scope"] == "01-2026"

    def test_edit_form_keeps_paymaster_available(self, _new_release):
        form = NewReleaseForm(instance=_new_release)

        assert _new_release.paymaster in form.fields["paymaster"].queryset
