from datetime import date

import pytest
from django.utils import timezone

from domains.gatehouse.exceptions import VisitorsRegisterError
from domains.gatehouse.models import VisitorsRegister
from domains.gatehouse.services import VisitorsRegisterService

pytestmark = pytest.mark.django_db


class TestVisitorsRegisterServiceCreate:

    def test_create_without_date_uses_server_today(self, visitor, admin_user):
        register = VisitorsRegisterService.create_visit_register(
            {"visitor": visitor}, user=admin_user
        )
        assert register.visitDate == timezone.localdate()
        assert register.created_by == admin_user
        assert register.is_active is True

    def test_create_without_user_keeps_audit_none(self, visitor):
        register = VisitorsRegisterService.create_visit_register(
            {"visitor": visitor, "visitDate": date(2026, 10, 5)}
        )
        assert register.visitDate == date(2026, 10, 5)
        assert register.created_by is None

    def test_create_with_explicit_date(self, visitor):
        register = VisitorsRegisterService.create_visit_register(
            {"visitor": visitor, "visitDate": date(2026, 10, 7)}
        )
        assert register.visitDate == date(2026, 10, 7)

    def test_create_accepts_visitor_pk(self, visitor):
        register = VisitorsRegisterService.create_visit_register(
            {"visitor": visitor.pk}
        )
        assert register.visitor == visitor

    def test_create_missing_visitor_raises(self, visitor):
        with pytest.raises(VisitorsRegisterError) as exc:
            VisitorsRegisterService.create_visit_register({})
        assert "visitor" in str(exc.value)

    def test_create_unknown_visitor_pk_raises(self):
        with pytest.raises(VisitorsRegisterError) as exc:
            VisitorsRegisterService.create_visit_register({"visitor": 999999})
        assert "Visitante não encontrado" in str(exc.value)

    def test_create_invalid_date_type_raises(self, visitor):
        with pytest.raises(VisitorsRegisterError) as exc:
            VisitorsRegisterService.create_visit_register(
                {"visitor": visitor, "visitDate": "não-é-data"}
            )
        assert "Data da visita inválida" in str(exc.value)

    def test_create_duplicate_raises(self, visitor):
        VisitorsRegisterService.create_visit_register(
            {"visitor": visitor, "visitDate": date(2026, 10, 5)}
        )
        with pytest.raises(VisitorsRegisterError) as exc:
            VisitorsRegisterService.create_visit_register(
                {"visitor": visitor, "visitDate": date(2026, 10, 5)}
            )
        assert "Já existe um registro de visita" in str(exc.value)
        assert VisitorsRegister.objects.count() == 1


class TestVisitorsRegisterServiceUpdate:

    @pytest.fixture
    def register(self, visitor):
        return VisitorsRegister.objects.create(
            visitor=visitor,
            visitDate=date(2026, 10, 5),
            observations="Original",
        )

    def test_update_changes_fields(self, register, other_visitor, admin_user):
        updated = VisitorsRegisterService.update_visit_register(
            register,
            {
                "visitor": other_visitor,
                "visitDate": date(2026, 10, 6),
                "observations": "Atualizado",
                "is_active": False,
            },
            user=admin_user,
        )
        updated.refresh_from_db()
        assert updated.visitor == other_visitor
        assert updated.visitDate == date(2026, 10, 6)
        assert updated.observations == "Atualizado"
        assert updated.is_active is False

    def test_update_sets_created_by_to_editor(
        self, register, admin_user, django_user_model
    ):
        creator = django_user_model.objects.create_user(
            username="criador", email="criador@teste.com", password="x"
        )
        register.created_by = creator
        register.save()
        updated = VisitorsRegisterService.update_visit_register(
            register, {"observations": "Editado"}, user=admin_user
        )
        updated.refresh_from_db()
        assert updated.created_by == admin_user
        assert updated.created_at is not None

    def test_update_without_user_keeps_created_by(
        self, register, admin_user
    ):
        register.created_by = admin_user
        register.save()
        updated = VisitorsRegisterService.update_visit_register(
            register, {"observations": "Sem usuário"}
        )
        updated.refresh_from_db()
        assert updated.created_by == admin_user

    def test_update_partial_keeps_missing_fields(self, register):
        updated = VisitorsRegisterService.update_visit_register(
            register, {"observations": "Parcial"}
        )
        updated.refresh_from_db()
        assert updated.visitDate == date(2026, 10, 5)
        assert updated.visitor == register.visitor
        assert updated.observations == "Parcial"

    def test_update_none_instance_raises(self):
        with pytest.raises(VisitorsRegisterError):
            VisitorsRegisterService.update_visit_register(
                None, {"observations": "x"}
            )

    def test_update_without_visit_date_raises(self, register):
        register.visitDate = None
        register.save()
        with pytest.raises(VisitorsRegisterError) as exc:
            VisitorsRegisterService.update_visit_register(register, {})
        assert "visitDate" in str(exc.value)

    def test_update_duplicate_on_other_record_raises(
        self, register, visitor
    ):
        VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 11, 1)
        )
        with pytest.raises(VisitorsRegisterError) as exc:
            VisitorsRegisterService.update_visit_register(
                register, {"visitDate": date(2026, 11, 1)}
            )
        assert "Já existe um registro de visita" in str(exc.value)

    def test_update_same_date_on_self_not_flagged(self, register):
        updated = VisitorsRegisterService.update_visit_register(
            register,
            {"visitDate": date(2026, 10, 5), "observations": "Mesma data"},
        )
        assert updated.pk == register.pk
        assert updated.observations == "Mesma data"


class TestVisitorsRegisterServiceDeleteAndQueries:

    def test_delete_removes_record(self, visitor):
        register = VisitorsRegisterService.create_visit_register(
            {"visitor": visitor}
        )
        VisitorsRegisterService.delete_visit_register(register)
        assert not VisitorsRegister.objects.filter(pk=register.pk).exists()

    def test_delete_none_raises(self):
        with pytest.raises(VisitorsRegisterError):
            VisitorsRegisterService.delete_visit_register(None)

    def test_get_all_returns_records(self, visitor, other_visitor):
        VisitorsRegisterService.create_visit_register(
            {"visitor": visitor, "visitDate": date(2026, 10, 5)}
        )
        VisitorsRegisterService.create_visit_register(
            {"visitor": other_visitor, "visitDate": date(2026, 10, 6)}
        )
        rows = list(VisitorsRegisterService.get_all_visit_registers())
        assert len(rows) == 2
        assert rows[0].visitDate >= rows[1].visitDate

    def test_get_all_empty(self):
        assert list(VisitorsRegisterService.get_all_visit_registers()) == []
