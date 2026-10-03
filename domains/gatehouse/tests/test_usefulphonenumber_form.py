from datetime import date

import pytest
from django import forms as django_forms

from domains.gatehouse.forms import ISODateInput, UsefulPhoneNumberForm
from domains.gatehouse.models import UsefulPhoneNumber
from domains.parameters.models import CategoryPhone

pytestmark = pytest.mark.django_db


class TestUsefulPhoneNumberForm:

    @pytest.fixture
    def category_phone(self):
        return CategoryPhone.objects.create(name="Emergencia")

    @pytest.fixture
    def inactive_category(self):
        return CategoryPhone.objects.create(name="Desativada", is_active=False)

    def _valid_data(self, condominium, category_phone, **overrides):
        data = {
            "condominium": condominium.pk,
            "categoryPhone": category_phone.pk,
            "releaseDate": "2026-10-02",
            "name": "Portao Geral",
            "phone1": "(11) 3333-4444",
            "phone2": "",
            "phone3": "",
            "phone4": "",
            "phone5": "",
            "observations": "",
        }
        data.update(overrides)
        return data

    def test_form_valid(self, condominium, category_phone):
        form = UsefulPhoneNumberForm(
            data=self._valid_data(condominium, category_phone)
        )
        assert form.is_valid()
        assert form.errors == {}
        assert form.cleaned_data["name"] == "Portao Geral"

    def test_required_fields(self, condominium, category_phone):
        for field in (
            "condominium",
            "categoryPhone",
            "releaseDate",
            "name",
            "phone1",
        ):
            data = self._valid_data(condominium, category_phone)
            del data[field]
            form = UsefulPhoneNumberForm(data=data)
            assert not form.is_valid(), field
            assert field in form.errors, field

    def test_optional_fields(self, condominium, category_phone):
        data = self._valid_data(
            condominium,
            category_phone,
            phone2="",
            phone3="",
            phone4="",
            phone5="",
            observations="",
        )
        form = UsefulPhoneNumberForm(data=data)
        assert form.is_valid()

    def test_category_and_date_required_even_though_nullable(self, condominium):
        assert UsefulPhoneNumberForm().fields["categoryPhone"].required is True
        assert UsefulPhoneNumberForm().fields["releaseDate"].required is True

    def test_name_is_stripped(self, condominium, category_phone):
        form = UsefulPhoneNumberForm(
            data=self._valid_data(condominium, category_phone, name="  Academia  ")
        )
        assert form.is_valid()
        assert form.cleaned_data["name"] == "Academia"

    def test_invalid_phone1_rejected(self, condominium, category_phone):
        form = UsefulPhoneNumberForm(
            data=self._valid_data(condominium, category_phone, phone1="123")
        )
        assert not form.is_valid()

    def test_invalid_phone2_rejected(self, condominium, category_phone):
        form = UsefulPhoneNumberForm(
            data=self._valid_data(condominium, category_phone, phone2="abc")
        )
        assert not form.is_valid()

    def test_digits_only_phone_accepted(self, condominium, category_phone):
        form = UsefulPhoneNumberForm(
            data=self._valid_data(condominium, category_phone, phone1="11999998888")
        )
        assert form.is_valid()

    def test_release_date_invalid_format(self, condominium, category_phone):
        form = UsefulPhoneNumberForm(
            data=self._valid_data(condominium, category_phone, releaseDate="nao-e-data")
        )
        assert not form.is_valid()
        assert "releaseDate" in form.errors

    def test_duplicate_rejected(self, condominium, category_phone):
        data = self._valid_data(condominium, category_phone)
        assert UsefulPhoneNumberForm(data=data).is_valid()
        UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="(11) 3333-4444",
        )
        form = UsefulPhoneNumberForm(data=data)
        assert not form.is_valid()

    def test_duplicate_different_name_allowed(self, condominium, category_phone):
        UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="(11) 3333-4444",
        )
        form = UsefulPhoneNumberForm(
            data=self._valid_data(condominium, category_phone, name="Portao Socorro")
        )
        assert form.is_valid()

    def test_duplicate_excludes_own_instance(self, condominium, category_phone):
        record = UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="(11) 3333-4444",
        )
        form = UsefulPhoneNumberForm(
            data=self._valid_data(condominium, category_phone),
            instance=record,
        )
        assert form.is_valid()

    def test_phone_widget_attrs(self):
        form = UsefulPhoneNumberForm()
        for field in ("phone1", "phone2", "phone3", "phone4", "phone5"):
            widget = form.fields[field].widget
            assert widget.attrs["class"] == "mask-phone"
            assert widget.attrs["placeholder"] == "(99) 99999-9999"

    def test_phone_help_text(self):
        form = UsefulPhoneNumberForm()
        for field in ("phone1", "phone2", "phone3", "phone4", "phone5"):
            assert "(99) 99999-9999" in form.fields[field].help_text

    def test_select_widget_attrs(self):
        form = UsefulPhoneNumberForm()
        for field in ("condominium", "categoryPhone"):
            widget = form.fields[field].widget
            assert isinstance(widget, django_forms.Select)
            assert "background-color: #ffffff" in widget.attrs["style"]

    def test_release_date_widget_is_iso_date_input(self, condominium, category_phone):
        record = UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="11999998888",
        )
        form = UsefulPhoneNumberForm(instance=record)
        widget = form.fields["releaseDate"].widget
        assert isinstance(widget, ISODateInput)
        rendered = str(form["releaseDate"])
        assert 'value="2026-10-02"' in rendered

    def test_queryset_excludes_inactive_condominium(
        self, condominium, inactive_condominium, category_phone
    ):
        form = UsefulPhoneNumberForm()
        pks = list(form.fields["condominium"].queryset.values_list("pk", flat=True))
        assert condominium.pk in pks
        assert inactive_condominium.pk not in pks

    def test_queryset_excludes_inactive_category(
        self, condominium, category_phone, inactive_category
    ):
        form = UsefulPhoneNumberForm()
        pks = list(form.fields["categoryPhone"].queryset.values_list("pk", flat=True))
        assert category_phone.pk in pks
        assert inactive_category.pk not in pks

    def test_queryset_keeps_selected_inactive_on_edit(
        self, condominium, inactive_category, category_phone
    ):
        record = UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="11999998888",
        )
        record.categoryPhone = inactive_category
        record.save()
        form = UsefulPhoneNumberForm(instance=record)
        pks = list(form.fields["categoryPhone"].queryset.values_list("pk", flat=True))
        assert inactive_category.pk in pks
