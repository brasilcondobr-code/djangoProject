from datetime import date, timedelta

import pytest
from django.utils import timezone

from domains.gatehouse.forms import VisitorsRegisterForm
from domains.gatehouse.models import VisitorsRegister

pytestmark = pytest.mark.django_db


def _data(visitor, **overrides):
    data = {
        "visitor": visitor.pk,
        "observations": "",
        "is_active": "on",
    }
    data.update(overrides)
    return data


class TestVisitorsRegisterForm:

    def test_create_valid_without_visit_date_fills_today(self, visitor):
        form = VisitorsRegisterForm(data=_data(visitor))
        assert form.is_valid(), form.errors
        assert form.cleaned_data["visitDate"] == timezone.localdate()

    def test_create_ignores_client_sent_date(self, visitor):
        tomorrow = timezone.localdate() + timedelta(days=1)
        form = VisitorsRegisterForm(
            data=_data(visitor, visitDate=tomorrow.isoformat())
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["visitDate"] == timezone.localdate()

    def test_create_widget_readonly_and_initial(self):
        form = VisitorsRegisterForm()
        field = form.fields["visitDate"]
        assert field.widget.attrs.get("readonly") == "readonly"
        assert field.initial == timezone.localdate()
        assert field.required is False

    def test_edit_widget_editable_and_required(self, visitor):
        register = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        form = VisitorsRegisterForm(instance=register)
        field = form.fields["visitDate"]
        assert "readonly" not in field.widget.attrs
        assert field.required is True

    def test_visitor_required(self, visitor):
        data = _data(visitor)
        del data["visitor"]
        form = VisitorsRegisterForm(data=data)
        assert not form.is_valid()
        assert "visitor" in form.errors
        assert "O visitante é obrigatório." in form.errors["visitor"]

    def test_observations_optional(self, visitor):
        form = VisitorsRegisterForm(
            data=_data(visitor, observations="   "),
        )
        assert form.is_valid(), form.errors

    def test_duplicate_visitor_and_date_rejected(self, visitor):
        VisitorsRegister.objects.create(
            visitor=visitor, visitDate=timezone.localdate()
        )
        form = VisitorsRegisterForm(data=_data(visitor))
        assert not form.is_valid()
        assert "visitDate" in form.errors
        assert "Já existe um registro de visita" in form.errors["visitDate"][0]

    def test_edit_same_record_not_flagged_as_duplicate(self, visitor):
        register = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        form = VisitorsRegisterForm(
            data=_data(visitor, visitDate="2026-10-05", observations="Editado"),
            instance=register,
        )
        assert form.is_valid(), form.errors

    def test_edit_can_change_visit_date(self, visitor):
        register = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        form = VisitorsRegisterForm(
            data=_data(visitor, visitDate="2026-10-08"),
            instance=register,
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["visitDate"] == date(2026, 10, 8)

    def test_edit_without_visit_date_rejected(self, visitor):
        register = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        form = VisitorsRegisterForm(data=_data(visitor), instance=register)
        assert not form.is_valid()
        assert "visitDate" in form.errors

    def test_invalid_visit_date_rejected_on_edit(self, visitor):
        register = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        form = VisitorsRegisterForm(
            data=_data(visitor, visitDate="não-é-data"),
            instance=register,
        )
        assert not form.is_valid()
        assert "visitDate" in form.errors

    def test_save_creates_record(self, visitor):
        form = VisitorsRegisterForm(data=_data(visitor, observations="Entrou"))
        assert form.is_valid(), form.errors
        register = form.save()
        assert register.pk is not None
        assert register.visitDate == timezone.localdate()
        assert register.observations == "Entrou"
        assert register.is_active is True

    def test_visitor_queryset_excludes_inactive(
        self, visitor, inactive_visitor
    ):
        form = VisitorsRegisterForm()
        pks = set(form.fields["visitor"].queryset.values_list("pk", flat=True))
        assert visitor.pk in pks
        assert inactive_visitor.pk not in pks

    def test_visitor_queryset_keeps_selected_inactive_on_edit(
        self, inactive_visitor
    ):
        register = VisitorsRegister.objects.create(
            visitor=inactive_visitor, visitDate=date(2026, 10, 5)
        )
        form = VisitorsRegisterForm(instance=register)
        pks = set(form.fields["visitor"].queryset.values_list("pk", flat=True))
        assert inactive_visitor.pk in pks

    def test_save_sets_audit_dates(self, visitor):
        form = VisitorsRegisterForm(data=_data(visitor))
        assert form.is_valid(), form.errors
        register = form.save()
        assert register.created_at is not None
        assert register.updated_at is not None
