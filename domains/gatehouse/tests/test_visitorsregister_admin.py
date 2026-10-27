from datetime import date

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.utils import timezone

from domains.gatehouse.admin import VisitorsRegisterAdmin
from domains.gatehouse.forms import VisitorsRegisterForm
from domains.gatehouse.models import VisitorsRegister

pytestmark = pytest.mark.django_db


class TestVisitorsRegisterAdminConfig:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = VisitorsRegisterAdmin(VisitorsRegister, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert global_admin.site.is_registered(VisitorsRegister)
        assert isinstance(self.admin, VisitorsRegisterAdmin)

    def test_form(self):
        assert self.admin.form == VisitorsRegisterForm

    def test_fieldsets_principal_fields_order(self):
        principal = self.admin.fieldsets[0]
        assert str(principal[0]) == "Principal"
        assert principal[1]["fields"] == (
            "visitor",
            "visitDate",
            "observations",
        )

    def test_fieldsets_auditoria_is_last_and_collapsed(self):
        auditoria = self.admin.fieldsets[-1]
        assert str(auditoria[0]) == "Auditoria"
        assert auditoria[1]["fields"] == (
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        )
        assert "collapse" in auditoria[1]["classes"]

    def test_jazzmin_section_order(self):
        assert self.admin.jazzmin_section_order == ["Principal", "Auditoria"]

    def test_readonly_audit_fields(self):
        assert self.admin.readonly_fields == (
            "created_by",
            "created_at",
            "updated_at",
        )

    def test_list_config(self):
        assert self.admin.list_display == (
            "id",
            "visitor",
            "visitDate",
            "is_active",
            "created_at",
        )
        assert self.admin.list_filter == ("visitor", "is_active", "visitDate")
        assert self.admin.search_fields == ("visitor__name", "observations")
        assert self.admin.ordering == ["-visitDate", "-id"]
        assert self.admin.list_per_page == 25

    def test_change_permission_not_overridden(self):
        assert (
            "has_change_permission"
            not in VisitorsRegisterAdmin.__dict__
        )

    def test_no_media_js(self):
        assert not hasattr(VisitorsRegisterAdmin, "Media")


class TestVisitorsRegisterAdminIntegration:

    def _login(self, client, admin_user):
        assert client.login(username="admin", password="admin123")

    def _payload(self, visitor, **overrides):
        data = {
            "visitor": str(visitor.pk),
            "observations": "Visita registrada",
            "is_active": "on",
            "_save": "Save",
        }
        data.update(overrides)
        return data

    def test_add_page_renders(self, client, admin_user, visitor):
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/visitorsregister/add/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Principal" in content
        assert "Auditoria" in content
        assert 'id="id_visitor"' in content
        assert 'id="id_visitDate"' in content
        date_line = next(
            line
            for line in content.splitlines()
            if 'id="id_visitDate"' in line
        )
        assert "readonly" in date_line
        assert 'type="date"' in date_line
        assert content.index('id="id_visitor"') < content.index(
            'id="id_visitDate"'
        )

    def test_create_assigns_server_today_and_created_by(
        self, client, admin_user, visitor
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/visitorsregister/add/", self._payload(visitor)
        )
        assert response.status_code == 302
        record = VisitorsRegister.objects.get()
        assert record.visitDate == timezone.localdate()
        assert record.visitor == visitor
        assert record.created_by == admin_user
        assert record.is_active is True

    def test_create_ignores_manipulated_visit_date(
        self, client, admin_user, visitor
    ):
        self._login(client, admin_user)
        payload = self._payload(visitor, visitDate="2020-01-01")
        response = client.post(
            "/admin/gatehouse/visitorsregister/add/", payload
        )
        assert response.status_code == 302
        record = VisitorsRegister.objects.get()
        assert record.visitDate == timezone.localdate()

    def test_create_without_visitor_is_rejected(
        self, client, admin_user, visitor
    ):
        self._login(client, admin_user)
        payload = self._payload(visitor)
        payload.pop("visitor")
        response = client.post(
            "/admin/gatehouse/visitorsregister/add/", payload
        )
        assert response.status_code == 200
        assert "O visitante é obrigatório." in response.content.decode()
        assert VisitorsRegister.objects.count() == 0

    def test_create_duplicate_is_rejected(
        self, client, admin_user, visitor
    ):
        self._login(client, admin_user)
        url = "/admin/gatehouse/visitorsregister/add/"
        assert client.post(url, self._payload(visitor)).status_code == 302
        response = client.post(url, self._payload(visitor))
        assert response.status_code == 200
        assert "Já existe um registro de visita" in response.content.decode()
        assert VisitorsRegister.objects.count() == 1

    def test_change_page_renders_visit_date_editable(
        self, client, admin_user, visitor
    ):
        record = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        self._login(client, admin_user)
        response = client.get(
            "/admin/gatehouse/visitorsregister/%s/change/" % record.pk
        )
        assert response.status_code == 200
        content = response.content.decode()
        date_line = next(
            line
            for line in content.splitlines()
            if 'id="id_visitDate"' in line
        )
        assert "readonly" not in date_line

    def test_edit_updates_visit_date_and_created_by(
        self, client, admin_user, visitor, django_user_model
    ):
        creator = django_user_model.objects.create_superuser(
            username="criador05",
            email="criador05@teste.com",
            password="criador05",
        )
        record = VisitorsRegister.objects.create(
            visitor=visitor,
            visitDate=date(2026, 10, 5),
            observations="Original",
            created_by=creator,
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/visitorsregister/%s/change/" % record.pk,
            self._payload(
                visitor,
                visitDate="2026-10-20",
                observations="Editado pelo admin",
            ),
        )
        assert response.status_code == 302
        record.refresh_from_db()
        assert record.visitDate == date(2026, 10, 20)
        assert record.observations == "Editado pelo admin"
        # decisão do módulo 05: created_by = usuário da última gravação
        assert record.created_by == admin_user
        assert record.created_by != creator

    def test_edit_without_visit_date_is_rejected(
        self, client, admin_user, visitor
    ):
        record = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        self._login(client, admin_user)
        payload = self._payload(visitor)
        payload.pop("visitDate", None)
        response = client.post(
            "/admin/gatehouse/visitorsregister/%s/change/" % record.pk,
            payload,
        )
        assert response.status_code == 200
        assert response.context["adminform"].form.errors
        record.refresh_from_db()
        assert record.visitDate == date(2026, 10, 5)

    def test_delete_via_post(self, client, admin_user, visitor):
        record = VisitorsRegister.objects.create(
            visitor=visitor, visitDate=date(2026, 10, 5)
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/visitorsregister/%s/delete/" % record.pk,
            {"post": "yes"},
        )
        assert response.status_code == 302
        assert not VisitorsRegister.objects.filter(pk=record.pk).exists()
