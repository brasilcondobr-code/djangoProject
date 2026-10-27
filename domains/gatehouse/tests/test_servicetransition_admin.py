from datetime import date

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin import TabularInline
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from domains.gatehouse.admin import ServiceTransitionAdmin, ServiceTransitionObjectInline
from domains.gatehouse.forms import ServiceTransitionForm, ServiceTransitionObjectForm
from domains.gatehouse.models import ServiceTransition

pytestmark = pytest.mark.django_db


class TestServiceTransitionAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = ServiceTransitionAdmin(ServiceTransition, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert global_admin.site.is_registered(ServiceTransition)
        assert isinstance(self.admin, ServiceTransitionAdmin)

    def test_admin_form(self):
        assert self.admin.form == ServiceTransitionForm

    def test_fieldsets_principal_fields_order(self):
        principal = self.admin.fieldsets[0]
        assert str(principal[0]) == "Principal"
        assert principal[1]["fields"] == (
            "condominium",
            "collaboratorEnd",
            "collaboratorStart",
            "releaseDate",
            "observations",
        )

    def test_fieldsets_auditoria_is_last_and_collapsed(self):
        auditoria = self.admin.fieldsets[-1]
        assert str(auditoria[0]) == "Auditoria"
        assert auditoria[1]["fields"] == ("is_active", "created_by", "created_at", "updated_at")
        assert "collapse" in auditoria[1]["classes"]

    def test_jazzmin_section_order(self):
        assert self.admin.jazzmin_section_order == ["Principal", "Objetos", "Auditoria"]

    def test_inline_configuration(self):
        assert self.admin.inlines == [ServiceTransitionObjectInline]
        inline = self.admin.inlines[0]
        assert issubclass(inline, TabularInline)
        assert inline.model._meta.model_name == "servicetransitionobject"
        assert inline.form == ServiceTransitionObjectForm
        assert inline.verbose_name_plural == "Objetos"
        assert inline.extra == 1
        assert inline.fields == (
            "categoryObj",
            "itemObj",
            "amountObj",
            "shiftDate",
        )

    def test_list_display(self):
        assert self.admin.list_display == (
            "id",
            "condominium",
            "collaboratorEnd",
            "collaboratorStart",
            "releaseDate",
            "is_active",
            "created_at",
        )

    def test_list_filter(self):
        assert self.admin.list_filter == ("condominium", "is_active", "releaseDate")

    def test_search_fields(self):
        assert self.admin.search_fields == (
            "condominium__name",
            "collaboratorEnd__name",
            "collaboratorStart__name",
            "observations",
        )

    def test_ordering(self):
        assert self.admin.ordering == ["-releaseDate", "-id"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ("created_by", "created_at", "updated_at")

    def test_list_per_page(self):
        assert self.admin.list_per_page == 25

    def test_media_includes_css_without_js(self):
        assert not getattr(self.admin.Media, "js", None)
        assert "gatehouse/css/servicetransition_admin.css" in self.admin.Media.css["all"]

    def test_save_model_sets_created_by(self, admin_user, condominium, collaborator_out, collaborator_in):
        request = self.factory.get("/admin/gatehouse/servicetransition/add/")
        request.user = admin_user
        transition = ServiceTransition(
            condominium=condominium,
            collaboratorEnd=collaborator_out,
            collaboratorStart=collaborator_in,
            releaseDate=date(2026, 9, 24),
        )
        self.admin.save_model(request, transition, form=None, change=False)
        assert transition.created_by == admin_user

    def test_save_model_edit_keeps_created_by(self, admin_user, transition, django_user_model):
        other_user = django_user_model.objects.create_user(username="outro", password="x")
        transition.created_by = other_user
        transition.save()

        request = self.factory.get("/admin/gatehouse/servicetransition/change/1/")
        request.user = admin_user
        transition.observations = "Atualizado"
        self.admin.save_model(request, transition, form=None, change=True)
        transition.refresh_from_db()
        assert transition.created_by == other_user

    def test_get_queryset_optimized(self, transition):
        request = self.factory.get("/admin/gatehouse/servicetransition/")
        request.user = None
        qs = self.admin.get_queryset(request)
        assert "condominium" in qs.query.select_related
        assert "collaboratorEnd" in qs.query.select_related
        assert "collaboratorStart" in qs.query.select_related
        assert "items" in qs._prefetch_related_lookups


class TestServiceTransitionAdminRender:

    def _login(self, client, admin_user):
        assert client.login(username="admin", password="admin123")

    def test_add_page_renders(self, client, admin_user, condominium, collaborator_out, collaborator_in):
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/servicetransition/add/")
        assert response.status_code == 200

        content = response.content.decode()

        assert 'id="servicetransition_form"' in content
        assert "gatehouse/css/servicetransition_admin.css" in content
        assert 'id="id_items-0-startTime"' not in content
        assert 'id="id_items-0-endTime"' not in content
        assert 'id="id_items-0-categoryObj"' in content

        import re

        from django.utils import timezone

        match = re.search(r'<input type="date" name="items-0-shiftDate"[^>]*value="([^"]*)"', content)
        assert match is not None, "input visivel type=date da Data do turno nao encontrado"
        assert match.group(1) == timezone.localdate().isoformat()
        assert str(condominium.name) in content
        assert str(collaborator_out.name) in content
        assert str(collaborator_in.name) in content

        principal_at = content.find("Principal")
        objetos_at = content.find("Objetos")
        auditoria_at = content.find("Auditoria")
        assert -1 < principal_at < objetos_at < auditoria_at

    def test_change_page_renders_existing_dates_as_iso(self, client, admin_user, transition, category):
        import re

        from domains.gatehouse.models import ServiceTransitionObject

        ServiceTransitionObject.objects.create(
            service_transition=transition,
            categoryObj=category,
            itemObj="Cadeira",
            amountObj=1,
            shiftDate=date(2026, 9, 25),
        )
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/servicetransition/%s/change/" % transition.pk)
        assert response.status_code == 200
        content = response.content.decode()

        release = re.search(r'<input type="date" name="releaseDate"[^>]*value="([^"]*)"', content)
        assert release is not None
        assert release.group(1) == "2026-09-24"

        shift = re.search(r'<input type="date" name="items-0-shiftDate"[^>]*value="([^"]*)"', content)
        assert shift is not None
        assert shift.group(1) == "2026-09-25"

        assert 'value="24/09/2026"' not in content
        assert 'value="25/09/2026"' not in content

    def test_css_targets_category_select_width(self):
        from django.contrib.staticfiles import finders

        css_path = finders.find("gatehouse/css/servicetransition_admin.css")
        assert css_path is not None
        with open(css_path, encoding="utf-8") as css_file:
            css = css_file.read()
        assert 'select[name$="-categoryObj"]' in css
        assert "width: 100%" in css

    def test_change_page_lists_objects_inline(self, client, admin_user, transition, category):
        self._login(client, admin_user)
        response = client.get(
            "/admin/gatehouse/servicetransition/%s/change/" % transition.pk
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert str(transition.condominium.name) in content
        assert "Objetos" in content

    def test_changelist_renders(self, client, admin_user, transition):
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/servicetransition/")
        assert response.status_code == 200
        content = response.content.decode()
        assert str(transition.condominium.name) in content

    def test_create_via_post_sets_created_by(self, client, admin_user, condominium, collaborator_out, collaborator_in, category):
        self._login(client, admin_user)
        payload = {
            "condominium": str(condominium.pk),
            "collaboratorEnd": str(collaborator_out.pk),
            "collaboratorStart": str(collaborator_in.pk),
            "releaseDate": "2026-09-24",
            "observations": "Criada via POST",
            "is_active": "on",
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-id": "",
            "items-0-service_transition": "",
            "items-0-categoryObj": str(category.pk),
            "items-0-itemObj": "Portao",
            "items-0-amountObj": "1",
            "items-0-shiftDate": "2026-09-24",
            "_save": "Salvar",
        }
        response = client.post("/admin/gatehouse/servicetransition/add/", payload, follow=False)
        assert response.status_code == 302

        transition = ServiceTransition.objects.get(observations="Criada via POST")
        assert transition.created_by == admin_user
        assert transition.items.count() == 1
        assert transition.items.first().itemObj == "Portao"
        assert str(transition.items.first().shiftDate) == "2026-09-24"

    def test_create_duplicate_is_rejected(self, client, admin_user, transition, collaborator_out, collaborator_in):
        self._login(client, admin_user)
        payload = {
            "condominium": str(transition.condominium_id),
            "collaboratorEnd": str(collaborator_out.pk),
            "collaboratorStart": str(collaborator_in.pk),
            "releaseDate": "2026-09-24",
            "observations": "Duplicada",
            "is_active": "on",
            "items-TOTAL_FORMS": "0",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "_save": "Salvar",
        }
        response = client.post("/admin/gatehouse/servicetransition/add/", payload)
        assert response.status_code == 200
        assert not ServiceTransition.objects.filter(observations="Duplicada").exists()
