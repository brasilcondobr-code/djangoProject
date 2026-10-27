from datetime import date

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from domains.gatehouse.admin import UsefulPhoneNumberAdmin
from domains.gatehouse.forms import UsefulPhoneNumberForm
from domains.gatehouse.models import UsefulPhoneNumber
from domains.parameters.models import CategoryPhone

pytestmark = pytest.mark.django_db


class TestUsefulPhoneNumberAdminConfig:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = UsefulPhoneNumberAdmin(UsefulPhoneNumber, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert global_admin.site.is_registered(UsefulPhoneNumber)
        assert isinstance(self.admin, UsefulPhoneNumberAdmin)

    def test_form(self):
        assert self.admin.form == UsefulPhoneNumberForm

    def test_fieldsets_principal_fields_order(self):
        principal = self.admin.fieldsets[0]
        assert str(principal[0]) == "Principal"
        assert principal[1]["fields"] == (
            "condominium",
            "categoryPhone",
            "releaseDate",
            "name",
            "phone1",
            "phone2",
            "phone3",
            "phone4",
            "phone5",
            "observations",
        )

    def test_fieldsets_auditoria_is_last_and_collapsed(self):
        auditoria = self.admin.fieldsets[-1]
        assert str(auditoria[0]) == "Auditoria"
        assert auditoria[1]["fields"] == ("is_active", "created_by", "created_at", "updated_at")
        assert "collapse" in auditoria[1]["classes"]

    def test_jazzmin_section_order(self):
        assert self.admin.jazzmin_section_order == ["Principal", "Auditoria"]

    def test_readonly_audit_fields(self):
        assert self.admin.readonly_fields == ("created_by", "created_at", "updated_at")

    def test_list_config(self):
        assert self.admin.list_display == (
            "id",
            "name",
            "condominium",
            "categoryPhone",
            "phone1",
            "releaseDate",
            "is_active",
        )
        assert self.admin.list_filter == ("condominium", "categoryPhone", "is_active")
        assert self.admin.search_fields == (
            "name",
            "phone1",
            "condominium__name",
            "categoryPhone__name",
        )
        assert self.admin.list_per_page == 25

    def test_media_js(self):
        js = self.admin.Media.js
        assert "js/utils.js" in js
        assert "js/gatehouse_usefulphone_admin.js" in js

    def test_has_change_permission_is_false(self, admin_user):
        request = self.factory.get("/admin/gatehouse/usefulphonenumber/")
        request.user = admin_user
        assert self.admin.has_change_permission(request) is False
        assert self.admin.has_change_permission(request, None) is False
        assert self.admin.has_add_permission(request) is True
        assert self.admin.has_view_permission(request) is True
        assert self.admin.has_delete_permission(request) is True

    def test_save_model_sets_created_by(self, admin_user, condominium):
        request = self.factory.get("/admin/gatehouse/usefulphonenumber/add/")
        request.user = admin_user
        phone = UsefulPhoneNumber(
            condominium=condominium,
            name="Portao",
            phone1="11999998888",
            releaseDate=date(2026, 10, 2),
        )
        self.admin.save_model(request, phone, form=None, change=False)
        assert phone.created_by == admin_user

    def test_get_queryset_optimized(self, condominium):
        request = self.factory.get("/admin/gatehouse/usefulphonenumber/")
        request.user = None
        qs = self.admin.get_queryset(request)
        assert "condominium" in qs.query.select_related
        assert "categoryPhone" in qs.query.select_related
        assert "created_by" in qs.query.select_related

    def test_no_csv_export_action(self):
        actions = getattr(self.admin, "actions", None) or []
        assert "export_as_csv" not in actions


class TestUsefulPhoneNumberAdminIntegration:

    def _login(self, client, admin_user):
        assert client.login(username="admin", password="admin123")

    def _payload(self, condominium, category_phone, **overrides):
        data = {
            "condominium": str(condominium.pk),
            "categoryPhone": str(category_phone.pk),
            "releaseDate": "2026-10-02",
            "name": "Portao Geral",
            "phone1": "(11) 3333-4444",
            "phone2": "",
            "phone3": "",
            "phone4": "",
            "phone5": "",
            "observations": "Registro de teste",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    @pytest.fixture
    def category_phone(self):
        return CategoryPhone.objects.create(name="Emergencia")

    def test_add_page_renders(self, client, admin_user, condominium, category_phone):
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/usefulphonenumber/add/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Principal" in content
        assert "Auditoria" in content
        assert 'id="id_condominium"' in content
        assert 'id="id_categoryPhone"' in content
        assert 'id="id_releaseDate"' in content
        assert 'id="id_phone1"' in content
        assert "mask-phone" in content
        assert "js/gatehouse_usefulphone_admin.js" in content

    def test_create_via_post_sets_created_by(
        self, client, admin_user, condominium, category_phone
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/usefulphonenumber/add/",
            self._payload(condominium, category_phone),
            follow=False,
        )
        assert response.status_code == 302
        record = UsefulPhoneNumber.objects.get(name="Portao Geral")
        assert record.created_by == admin_user
        assert record.phone1 == "(11) 3333-4444"
        assert record.categoryPhone == category_phone
        assert str(record.releaseDate) == "2026-10-02"

    def test_create_duplicate_is_rejected(
        self, client, admin_user, condominium, category_phone
    ):
        self._login(client, admin_user)
        url = "/admin/gatehouse/usefulphonenumber/add/"
        client.post(url, self._payload(condominium, category_phone))
        response = client.post(
            url, self._payload(condominium, category_phone, phone1="11999997777")
        )
        assert response.status_code == 200
        assert response.context["adminform"].form.errors
        assert UsefulPhoneNumber.objects.filter(name="Portao Geral").count() == 1

    def test_create_with_invalid_phone_shows_error(
        self, client, admin_user, condominium, category_phone
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/usefulphonenumber/add/",
            self._payload(condominium, category_phone, phone1="123"),
        )
        assert response.status_code == 200
        assert response.context["adminform"].form.errors

    def test_change_page_get_renders_read_only(
        self, client, admin_user, condominium, category_phone
    ):
        record = UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="(11) 3333-4444",
        )
        self._login(client, admin_user)
        response = client.get(
            "/admin/gatehouse/usefulphonenumber/%s/change/" % record.pk
        )
        assert response.status_code == 200
        assert "Portao Geral" in response.content.decode()

    def test_change_page_post_is_blocked(
        self, client, admin_user, condominium, category_phone
    ):
        record = UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="(11) 3333-4444",
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/usefulphonenumber/%s/change/" % record.pk,
            self._payload(condominium, category_phone, name="Alterado"),
        )
        assert response.status_code == 403
        record.refresh_from_db()
        assert record.name == "Portao Geral"

    def test_delete_flow(
        self, client, admin_user, condominium, category_phone
    ):
        record = UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="(11) 3333-4444",
        )
        self._login(client, admin_user)
        url = "/admin/gatehouse/usefulphonenumber/%s/delete/" % record.pk
        confirm = client.get(url)
        assert confirm.status_code == 200
        response = client.post(url, {"post": "yes"})
        assert response.status_code == 302
        assert not UsefulPhoneNumber.objects.filter(pk=record.pk).exists()

    def test_changelist_renders(self, client, admin_user, condominium, category_phone):
        UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate=date(2026, 10, 2),
            name="Portao Geral",
            phone1="(11) 3333-4444",
        )
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/usefulphonenumber/")
        assert response.status_code == 200
        assert "Portao Geral" in response.content.decode()
