from datetime import datetime

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.utils import timezone
from django.utils.timezone import make_aware

from domains.gatehouse.admin import OccurrenceAdmin
from domains.gatehouse.forms import OccurrenceForm
from domains.gatehouse.models import Occurrence
from domains.gatehouse.services import OccurrenceService

pytestmark = pytest.mark.django_db


class TestOccurrenceAdminConfig:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = OccurrenceAdmin(Occurrence, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert global_admin.site.is_registered(Occurrence)
        assert isinstance(self.admin, OccurrenceAdmin)

    def test_form(self):
        assert self.admin.form == OccurrenceForm

    def test_fieldsets_principal_fields_order(self):
        principal = self.admin.fieldsets[0]
        assert str(principal[0]) == "Principal"
        assert principal[1]["fields"] == (
            "unit",
            "releaseDate",
            "subject",
            "participants",
            "description",
        )

    def test_fieldsets_auditoria_is_last_and_collapsed(self):
        auditoria = self.admin.fieldsets[-1]
        assert str(auditoria[0]) == "Auditoria"
        assert auditoria[1]["fields"] == (
            "is_active",
            "created_user",
            "created_at",
            "updated_at",
        )
        assert "collapse" in auditoria[1]["classes"]

    def test_jazzmin_section_order(self):
        assert self.admin.jazzmin_section_order == ["Principal", "Auditoria"]

    def test_readonly_audit_fields(self):
        assert self.admin.readonly_fields == (
            "created_user",
            "created_at",
            "updated_at",
        )

    def test_list_config(self):
        assert self.admin.list_display == (
            "id",
            "unit",
            "releaseDate",
            "subject",
            "is_active",
            "created_at",
        )
        assert self.admin.list_filter == ("unit", "is_active")
        assert self.admin.search_fields == (
            "subject",
            "description",
            "unit__unit_number",
            "unit__condominium__name",
        )
        assert self.admin.ordering == ["-releaseDate", "-id"]
        assert self.admin.list_per_page == 25

    def test_filter_horizontal_participants(self):
        assert self.admin.filter_horizontal == ("participants",)

    def test_change_permission_not_overridden(self):
        assert "has_change_permission" not in OccurrenceAdmin.__dict__

    def test_no_media_js(self):
        assert not hasattr(OccurrenceAdmin, "Media")


class TestOccurrenceAdminIntegration:

    def _login(self, client, admin_user):
        assert client.login(username="admin", password="admin123")

    def _payload(self, unit=None, **overrides):
        data = {
            "subject": "Ocorrência registrada na portaria",
            "is_active": "on",
            "_save": "Save",
        }
        if unit is not None:
            data["unit"] = str(unit.pk)
        data.update(overrides)
        return data

    def test_add_page_renders(self, client, admin_user, unit):
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/occurrence/add/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Principal" in content
        assert "Auditoria" in content
        assert 'id="id_unit"' in content
        assert 'id="id_releaseDate"' in content
        assert 'id="id_subject"' in content
        assert 'name="participants"' in content
        assert "multiple" in content
        date_line = next(
            line
            for line in content.splitlines()
            if 'id="id_releaseDate"' in line
        )
        assert "readonly" in date_line
        assert 'type="datetime-local"' in date_line
        assert content.index('id="id_unit"') < content.index(
            'id="id_releaseDate"'
        )
        assert content.index('id="id_releaseDate"') < content.index(
            'id="id_subject"'
        )

    def test_create_assigns_server_now_and_created_user(
        self, client, admin_user, unit
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/occurrence/add/", self._payload(unit)
        )
        assert response.status_code == 302
        record = Occurrence.objects.get()
        diff = abs(record.releaseDate - timezone.now())
        assert diff.total_seconds() < 60
        assert record.releaseDate.second == 0
        assert record.unit == unit
        assert record.subject == "Ocorrência registrada na portaria"
        assert record.created_user == admin_user
        assert record.is_active is True

    def test_create_ignores_manipulated_datetime(
        self, client, admin_user, unit
    ):
        self._login(client, admin_user)
        payload = self._payload(unit, releaseDate="2020-01-01T10:00")
        response = client.post(
            "/admin/gatehouse/occurrence/add/", payload
        )
        assert response.status_code == 302
        record = Occurrence.objects.get()
        diff = abs(record.releaseDate - timezone.now())
        assert diff.total_seconds() < 60

    def test_create_without_subject_is_rejected(
        self, client, admin_user, unit
    ):
        self._login(client, admin_user)
        payload = self._payload(unit)
        payload.pop("subject")
        response = client.post(
            "/admin/gatehouse/occurrence/add/", payload
        )
        assert response.status_code == 200
        assert "O assunto é obrigatório." in response.content.decode()
        assert Occurrence.objects.count() == 0

    def test_create_duplicate_is_rejected(self, client, admin_user, unit):
        self._login(client, admin_user)
        Occurrence.objects.create(
            unit=unit,
            releaseDate=OccurrenceService.server_now(),
            subject="Ocorrência registrada na portaria",
        )
        response = client.post(
            "/admin/gatehouse/occurrence/add/", self._payload(unit)
        )
        assert response.status_code == 200
        assert "Já existe uma ocorrência" in response.content.decode()
        assert Occurrence.objects.count() == 1

    def test_create_with_participants(self, client, admin_user, unit, participant_a, participant_b):
        self._login(client, admin_user)
        payload = self._payload(
            unit,
            participants=[str(participant_a.pk), str(participant_b.pk)],
        )
        response = client.post(
            "/admin/gatehouse/occurrence/add/", payload
        )
        assert response.status_code == 302
        record = Occurrence.objects.get()
        names = set(record.participants.values_list("name", flat=True))
        assert names == {"Participante A", "Participante B"}

    def test_create_participant_from_other_condominium_rejected(
        self, client, admin_user, unit, foreign_participant
    ):
        self._login(client, admin_user)
        payload = self._payload(unit, participants=[str(foreign_participant.pk)])
        response = client.post(
            "/admin/gatehouse/occurrence/add/", payload
        )
        assert response.status_code == 200
        assert "devem pertencer" in response.content.decode()
        assert Occurrence.objects.count() == 0

    def test_create_unit_optional(self, client, admin_user):
        self._login(client, admin_user)
        payload = self._payload()
        payload["subject"] = "Sem unidade"
        response = client.post(
            "/admin/gatehouse/occurrence/add/", payload
        )
        assert response.status_code == 302
        record = Occurrence.objects.get()
        assert record.unit is None
        assert record.releaseDate is not None

    def test_change_page_renders_datetime_editable(
        self, client, admin_user, unit
    ):
        record = Occurrence.objects.create(
            unit=unit,
            releaseDate=make_aware(datetime(2026, 10, 5, 14, 30)),
            subject="Para editar",
        )
        self._login(client, admin_user)
        response = client.get(
            "/admin/gatehouse/occurrence/%s/change/" % record.pk
        )
        assert response.status_code == 200
        date_line = next(
            line
            for line in response.content.decode().splitlines()
            if 'id="id_releaseDate"' in line
        )
        assert "readonly" not in date_line

    def test_edit_updates_datetime_and_created_user(
        self, client, admin_user, unit, django_user_model
    ):
        creator = django_user_model.objects.create_superuser(
            username="criador07",
            email="criador07@teste.com",
            password="criador07",
        )
        record = Occurrence.objects.create(
            unit=unit,
            releaseDate=make_aware(datetime(2026, 10, 5, 14, 30)),
            subject="Original",
            created_user=creator,
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/occurrence/%s/change/" % record.pk,
            self._payload(
                unit,
                subject="Original",
                releaseDate="2026-12-24T09:00",
                description="Editada pelo admin",
            ),
        )
        assert response.status_code == 302
        record.refresh_from_db()
        assert record.releaseDate == make_aware(datetime(2026, 12, 24, 9, 0))
        assert record.description == "Editada pelo admin"
        # decisão do módulo 07: created_user = usuário da última gravação
        assert record.created_user == admin_user
        assert record.created_user != creator

    def test_edit_without_datetime_is_rejected(
        self, client, admin_user, unit
    ):
        record = Occurrence.objects.create(
            unit=unit,
            releaseDate=make_aware(datetime(2026, 10, 5, 14, 30)),
            subject="Exigir data",
        )
        self._login(client, admin_user)
        payload = self._payload(unit, subject="Exigir data")
        payload.pop("releaseDate", None)
        response = client.post(
            "/admin/gatehouse/occurrence/%s/change/" % record.pk, payload
        )
        assert response.status_code == 200
        assert response.context["adminform"].form.errors
        record.refresh_from_db()
        assert record.releaseDate == make_aware(datetime(2026, 10, 5, 14, 30))

    def test_delete_via_post(self, client, admin_user, unit):
        record = Occurrence.objects.create(
            unit=unit,
            releaseDate=make_aware(datetime(2026, 10, 5, 14, 30)),
            subject="Apagar",
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/occurrence/%s/delete/" % record.pk,
            {"post": "yes"},
        )
        assert response.status_code == 302
        assert not Occurrence.objects.filter(pk=record.pk).exists()
