from datetime import date
from decimal import Decimal

import pytest
from django.forms.models import inlineformset_factory
from django.utils import timezone

from domains.financial.forms import (
    CollectionCreditForm,
    CollectionCreditFormSet,
    CollectionForm,
    CollectionPaymentForm,
)
from domains.financial.models import Collection, CollectionCredit


def _credit_management_data(**row):
    data = {
        "credits-TOTAL_FORMS": "1",
        "credits-INITIAL_FORMS": "0",
        "credits-MIN_NUM_FORMS": "0",
        "credits-MAX_NUM_FORMS": "1000",
    }
    data.update(
        {f"credits-0-{name}": value for name, value in row.items()}
    )
    return data


def _credit_formset(collection, data):
    factory = inlineformset_factory(
        Collection,
        CollectionCredit,
        form=CollectionCreditForm,
        formset=CollectionCreditFormSet,
        extra=1,
        fields=("financialTransaction", "creditDate", "amountCredit"),
    )
    return factory(data=data, instance=collection)


def _form_data(unit, **overrides):
    data = {
        "condominium": unit.pk,
        "scope": "01-2026",
        "originalValue": "1.000,00",
        "discountPercent": "10,00",
        "penaltyPercent": "2,00",
        "feesPercent": "1,00",
        "chargesPercent": "0,50",
        "discountDeadline": "2026-01-10",
        "dueDate": "2099-01-10",
        "is_active": "on",
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestCollectionForm:

    def test_valid_form_normalizes_scope_and_values(self, _unit):
        form = CollectionForm(data=_form_data(_unit))

        assert form.is_valid(), form.errors
        cleaned = form.cleaned_data
        assert cleaned["scope"] == date(2026, 1, 1)
        assert str(cleaned["originalValue"]) == "1000.00"
        assert str(cleaned["discountPercent"]) == "10.00"
        assert str(cleaned["penaltyPercent"]) == "2.00"
        assert str(cleaned["feesPercent"]) == "1.00"
        assert str(cleaned["chargesPercent"]) == "0.50"

    def test_new_form_defaults_scope_to_current_month(self):
        form = CollectionForm()
        expected = timezone.localdate().strftime("%m-%Y")

        assert form.initial["scope"] == expected

    def test_new_form_presents_current_billing_date(self):
        form = CollectionForm()

        assert form.instance.billingDate == timezone.localdate()

    def test_discount_percent_is_limited_to_six_characters(self):
        form = CollectionForm()

        assert form.fields["discountPercent"].max_length == 6
        assert 'maxlength="6"' in str(form["discountPercent"])

    def test_discount_percent_rejects_more_than_six_characters(self, _unit):
        form = CollectionForm(
            data=_form_data(_unit, discountPercent="100,000")
        )

        assert not form.is_valid()
        assert "discountPercent" in form.errors

    def test_clean_refreshes_total_and_balance(self, _unit):
        form = CollectionForm(data=_form_data(_unit))

        assert form.is_valid(), form.errors
        assert form.instance.totalAmount == Decimal("935.00")
        assert form.instance.balance == Decimal("935.00")

    @pytest.mark.parametrize("raw_scope", ["2026-01", "1-2026", "13-2026"])
    def test_invalid_scope_formats(self, _unit, raw_scope):
        form = CollectionForm(data=_form_data(_unit, scope=raw_scope))

        assert not form.is_valid()
        assert "scope" in form.errors

    def test_required_dates(self, _unit):
        form = CollectionForm(
            data=_form_data(_unit, discountDeadline="", dueDate="")
        )

        assert not form.is_valid()
        assert "discountDeadline" in form.errors
        assert "dueDate" in form.errors

    def test_percent_above_one_hundred_is_rejected(self, _unit):
        form = CollectionForm(
            data=_form_data(_unit, discountPercent="100,01")
        )

        assert not form.is_valid()
        assert "discountPercent" in form.errors

    def test_negative_original_value_is_rejected(self, _unit):
        form = CollectionForm(data=_form_data(_unit, originalValue="-1,00"))

        assert not form.is_valid()
        assert "originalValue" in form.errors

    def test_original_value_is_optional(self, _unit):
        form = CollectionForm(data=_form_data(_unit, originalValue=""))

        assert form.is_valid(), form.errors
        assert form.cleaned_data["originalValue"] is None

    def test_duplicate_combination_is_rejected_on_add(self, _unit, _user):
        Collection.objects.create(
            condominium=_unit,
            billingDate=timezone.localdate(),
            scope=date(2026, 1, 1),
            discountDeadline=date(2026, 1, 10),
            dueDate=date(2099, 1, 10),
            created_by=_user,
            updated_by=_user,
        )

        form = CollectionForm(data=_form_data(_unit))

        assert not form.is_valid()
        assert "Já existe uma cobrança" in str(form.non_field_errors())

    def test_initial_values_are_formatted(self, _collection):
        form = CollectionForm(instance=_collection)

        assert form.initial["scope"] == "01-2026"
        assert form.initial["originalValue"] == "1.000,00"
        assert form.initial["discountPercent"] == "10,00"


@pytest.mark.django_db
class TestCollectionPaymentForm:

    def test_valid_payment_within_balance(
        self, _collection, _financial_transaction
    ):
        form = CollectionPaymentForm(
            data={
                "collection": _collection.pk,
                "financialTransaction": _financial_transaction.pk,
                "dateReceived": "2026-01-20",
                "amountReceived": "400,00",
            },
            collections=Collection.objects.filter(pk=_collection.pk),
        )

        assert form.is_valid(), form.errors
        assert str(form.cleaned_data["amountReceived"]) == "400.00"

    def test_amount_above_balance_is_rejected(
        self, _collection, _financial_transaction
    ):
        form = CollectionPaymentForm(
            data={
                "collection": _collection.pk,
                "financialTransaction": _financial_transaction.pk,
                "dateReceived": "2026-01-20",
                "amountReceived": "1.000,00",
            },
            collections=Collection.objects.filter(pk=_collection.pk),
        )

        assert not form.is_valid()
        assert "amountReceived" in form.errors

    def test_zero_amount_is_rejected(
        self, _collection, _financial_transaction
    ):
        form = CollectionPaymentForm(
            data={
                "collection": _collection.pk,
                "financialTransaction": _financial_transaction.pk,
                "dateReceived": "2026-01-20",
                "amountReceived": "0,00",
            },
            collections=Collection.objects.filter(pk=_collection.pk),
        )

        assert not form.is_valid()
        assert "amountReceived" in form.errors

    def test_collection_queryset_is_restricted(
        self, _collection, _financial_transaction
    ):
        form = CollectionPaymentForm(
            collections=Collection.objects.none()
        )

        assert not form.fields["collection"].queryset.exists()

    def test_amount_received_uses_same_mask_as_original_value(self):
        payment_field = CollectionPaymentForm()["amountReceived"].field
        payment_attrs = payment_field.widget.attrs
        original_attrs = CollectionForm()["originalValue"].field.widget.attrs

        for attr in ("class", "placeholder", "inputmode", "autocomplete"):
            assert payment_attrs[attr] == original_attrs[attr]


@pytest.mark.django_db
class TestCollectionCreditForm:

    def test_valid_credit(self, _financial_transaction):
        form = CollectionCreditForm(
            data={
                "financialTransaction": _financial_transaction.pk,
                "creditDate": "2026-01-20",
                "amountCredit": "100,00",
            }
        )

        assert form.is_valid(), form.errors
        assert str(form.cleaned_data["amountCredit"]) == "100.00"

    def test_zero_credit_is_rejected(self, _financial_transaction):
        form = CollectionCreditForm(
            data={
                "financialTransaction": _financial_transaction.pk,
                "creditDate": "2026-01-20",
                "amountCredit": "0,00",
            }
        )

        assert not form.is_valid()
        assert "amountCredit" in form.errors

    def test_credit_date_defaults_to_today(self, _financial_transaction):
        form = CollectionCreditForm()

        assert form.initial["creditDate"] == timezone.localdate()

    def test_credit_fields_are_not_required(self):
        form = CollectionCreditForm()

        assert form.fields["financialTransaction"].required is False
        assert form.fields["amountCredit"].required is False
        assert "required" not in str(form["financialTransaction"])
        assert "required" not in str(form["amountCredit"])

    def test_empty_credit_row_is_accepted(self, _collection):
        formset = _credit_formset(_collection, _credit_management_data())

        assert formset.is_valid(), formset.errors
        assert not formset.has_changed()

    def test_credit_row_with_only_date_is_ignored(self, _collection):
        data = _credit_management_data(
            creditDate=timezone.localdate().isoformat()
        )

        formset = _credit_formset(_collection, data)

        assert formset.is_valid(), formset.errors
        assert not formset.has_changed()

    def test_credit_row_with_operation_requires_amount(
        self, _collection, _financial_transaction
    ):
        data = _credit_management_data(
            financialTransaction=_financial_transaction.pk,
            creditDate="2026-01-20",
        )

        formset = _credit_formset(_collection, data)

        assert not formset.is_valid()
        assert "amountCredit" in formset.forms[0].errors

    def test_credit_row_with_amount_requires_operation(self, _collection):
        data = _credit_management_data(
            creditDate="2026-01-20",
            amountCredit="100,00",
        )

        formset = _credit_formset(_collection, data)

        assert not formset.is_valid()
        assert "financialTransaction" in formset.forms[0].errors
