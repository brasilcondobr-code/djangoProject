from datetime import date

import pytest
from django.db import IntegrityError, transaction

from domains.gatehouse.models import VisitorsRegister
from domains.residents.models import Visitor

pytestmark = pytest.mark.django_db


class TestVisitorsRegisterModel:

    @pytest.fixture
    def register(self, visitor):
        return VisitorsRegister.objects.create(
            visitor=visitor,
            visitDate=date(2026, 10, 5),
            observations="Visita agendada",
        )

    def test_create_and_str(self, register, visitor):
        assert register.pk is not None
        text = str(register)
        assert text.startswith("Visita 2026-10-05 — ")
        assert visitor.name in text

    def test_str_without_visitor_falls_back(self):
        assert str(VisitorsRegister()) == "05. Reg. Visitante"

    def test_meta_verbose(self):
        assert str(VisitorsRegister._meta.verbose_name) == "05. Reg. Visitante"
        assert (
            str(VisitorsRegister._meta.verbose_name_plural)
            == "05. Reg. Visitantes"
        )
        assert VisitorsRegister._meta.app_label == "gatehouse"

    def test_ordering(self):
        assert VisitorsRegister._meta.ordering == ["-visitDate", "-id"]

    def test_unique_constraint(self):
        constraint = VisitorsRegister._meta.constraints[0]
        assert constraint.name == "uniq_visitreg_visitor_date"
        assert tuple(constraint.fields) == ("visitor", "visitDate")

    def test_duplicate_visitor_date_blocked_by_db(self, visitor):
        VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                VisitorsRegister.objects.create(
                    visitor=visitor, visitDate=date(2026, 10, 5)
                )

    def test_same_visitor_other_date_allowed(self, visitor):
        VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        second = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 6)
        )
        assert second.pk is not None

    def test_field_rules(self):
        get = VisitorsRegister._meta.get_field
        assert get("visitor").null is False
        assert get("visitor").blank is False
        assert get("visitor").remote_field.related_name == "visit_registers"
        assert get("visitor").related_model is Visitor
        assert get("visitDate").null is True
        assert get("visitDate").blank is True
        assert get("observations").null is True
        assert get("observations").blank is True
        assert get("is_active").default is True
        assert get("created_by").editable is False
        assert get("created_by").null is True
        assert get("created_at").auto_now_add is True
        assert get("updated_at").auto_now is True

    def test_default_is_active_and_audit_null_without_user(self, visitor):
        register = VisitorsRegister.objects.create(visitor=visitor)
        assert register.is_active is True
        assert register.created_by is None
        assert register.visitDate is None

    def test_reverse_relation_accessor(self, register, visitor):
        assert list(visitor.visit_registers.all()) == [register]
