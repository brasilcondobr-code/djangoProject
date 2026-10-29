from datetime import date

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from domains.reservations.admin import MaintenanceReservationsAdmin
from domains.reservations.forms import MaintenanceReservationsForm
from domains.reservations.models import MaintenanceReservations

pytestmark = pytest.mark.django_db


def _admin():
    return MaintenanceReservationsAdmin(MaintenanceReservations, AdminSite())


def _request(factory, user):
    request = factory.post("/admin/reservations/maintenancereservations/")
    request.user = user
    setattr(request, "session", "session")
    setattr(request, "_messages", FallbackStorage(request))
    return request


def _messages(request):
    return [m.message for m in request._messages]


def _payload(unit, maintenance_type, **overrides):
    data = {
        "condominium": str(unit.pk),
        "typesOfMaintenance": str(maintenance_type.pk),
        "startDate": "2026-11-10",
        "endDate": "2026-11-15",
        "applicant": "Solicitante Admin",
        "observations": "",
        "is_active": "on",
        "_save": "Salvar",
    }
    data.update(overrides)
    return data


def _factory(unit, maintenance_type, **overrides):
    data = {
        "condominium": unit,
        "typesOfMaintenance": maintenance_type,
        "startDate": date(2026, 11, 10),
        "endDate": date(2026, 11, 15),
        "applicant": "Solicitante Admin",
    }
    data.update(overrides)
    return MaintenanceReservations.objects.create(**data)


class TestMaintenanceReservationsAdminConfig:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = MaintenanceReservationsAdmin(
            MaintenanceReservations, self.site
        )
        self.factory = RequestFactory()

    def test_registered(self):
        assert global_admin.site.is_registered(MaintenanceReservations)

    def test_admin_form(self):
        assert self.admin.form == MaintenanceReservationsForm

    def test_list_display(self):
        assert self.admin.list_display == (
            "id",
            "condominium",
            "typesOfMaintenance",
            "startDate",
            "endDate",
            "applicant",
            "status",
            "is_active",
        )

    def test_list_display_links(self):
        assert self.admin.list_display_links == ("id", "applicant")

    def test_list_filter(self):
        assert self.admin.list_filter == (
            "typesOfMaintenance",
            "status",
            "is_active",
            "condominium__condominium",
        )

    def test_search_fields(self):
        assert self.admin.search_fields == (
            "applicant",
            "condominium__unit_number",
            "condominium__tower",
            "condominium__condominium__name",
            "typesOfMaintenance__description",
        )

    def test_ordering(self):
        assert self.admin.ordering == ("-startDate", "-id")

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == (
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def test_list_per_page(self):
        assert self.admin.list_per_page == 25

    def test_empty_value_display(self):
        assert self.admin.empty_value_display == "-"

    def test_jazzmin_section_order(self):
        assert self.admin.jazzmin_section_order == ["Principal", "Auditoria"]

    def test_fieldsets(self):
        assert self.admin.fieldsets[0][0] == "Principal"
        assert self.admin.fieldsets[0][1]["fields"] == (
            "condominium",
            "typesOfMaintenance",
            "startDate",
            "endDate",
            "applicant",
            "observations",
        )
        assert self.admin.fieldsets[1][0] == "Auditoria"
        assert self.admin.fieldsets[1][1]["classes"] == ("collapse",)
        assert self.admin.fieldsets[1][1]["fields"] == (
            "is_active",
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def test_actions_registered(self):
        assert self.admin.actions == (
            "executar_manutencoes",
            "finalizar_manutencoes",
        )

    def test_action_descriptions(self):
        assert (
            self.admin.executar_manutencoes.short_description
            == "Executar manutenções selecionadas"
        )
        assert (
            self.admin.finalizar_manutencoes.short_description
            == "Finalizar manutenções selecionadas"
        )

    def test_media_includes_date_script(self):
        assert "js/maintenance_reservations_admin.js" in str(self.admin.media)

    def test_change_permission_only_agendamento(
        self, unit, maintenance_type, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        agendamento = _factory(unit, maintenance_type)
        execucao = _factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.EXECUCAO,
        )
        finalizado = _factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        assert admin.has_change_permission(request, agendamento) is True
        assert admin.has_change_permission(request, execucao) is False
        assert admin.has_change_permission(request, finalizado) is False

    def test_readonly_all_fields_outside_agendamento(
        self, unit, maintenance_type, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        agendamento = _factory(unit, maintenance_type)
        execucao = _factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.EXECUCAO,
        )

        assert admin.get_readonly_fields(request, agendamento) == [
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        assert set(admin.get_readonly_fields(request, execucao)) == {
            field.name for field in MaintenanceReservations._meta.fields
        }

    def test_save_model_new_sets_server_status_and_audit(
        self, unit, maintenance_type, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        maintenance = MaintenanceReservations(
            condominium=unit,
            typesOfMaintenance=maintenance_type,
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 15),
            applicant="Solicitante Admin",
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        admin.save_model(request, maintenance, form=None, change=False)

        assert maintenance.pk is not None
        assert maintenance.status == MaintenanceReservations.Status.AGENDAMENTO
        assert maintenance.created_by == admin_user
        assert maintenance.updated_by == admin_user

    def test_execute_action_reports_success_and_failure(
        self, unit, maintenance_type, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        agendada = _factory(unit, maintenance_type)
        finalizada = _factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )

        queryset = MaintenanceReservations.objects.filter(
            pk__in=[agendada.pk, finalizada.pk]
        )
        admin.executar_manutencoes(request, queryset)

        agendada.refresh_from_db()
        assert agendada.status == MaintenanceReservations.Status.EXECUCAO
        messages = _messages(request)
        assert any("1 manutenção(ões) executada(s) com sucesso" in m for m in messages)
        assert any(f"#{finalizada.pk}:" in m for m in messages)

    def test_finalize_action_reports_success_and_failure(
        self, unit, maintenance_type, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        em_execucao = _factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.EXECUCAO,
        )
        agendada = _factory(unit, maintenance_type)

        queryset = MaintenanceReservations.objects.filter(
            pk__in=[em_execucao.pk, agendada.pk]
        )
        admin.finalizar_manutencoes(request, queryset)

        em_execucao.refresh_from_db()
        assert (
            em_execucao.status == MaintenanceReservations.Status.FINALIZADO
        )
        messages = _messages(request)
        assert any("1 manutenção(ões) finalizada(s) com sucesso" in m for m in messages)
        assert any(f"#{agendada.pk}:" in m for m in messages)

    def test_action_with_empty_queryset_reports_nothing(
        self, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        admin.executar_manutencoes(
            request, MaintenanceReservations.objects.none()
        )
        assert "Nenhuma manutenção selecionada." in _messages(request)


class TestMaintenanceReservationsAdminRender:

    @pytest.fixture(autouse=True)
    def setup(self, client, django_user_model):
        self.client = client
        self.user = django_user_model.objects.create_superuser(
            username="admin_mnt", email="admin_mnt@teste.com", password="admin123"
        )
        assert self.client.login(username="admin_mnt", password="admin123")

    def test_add_page_renders(self):
        response = self.client.get(
            "/admin/reservations/maintenancereservations/add/"
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "Nome do solicitante" in content
        assert "Principal" in content
        assert "Auditoria" in content

    def test_changelist_renders(self, unit, maintenance_type):
        _factory(unit, maintenance_type)
        response = self.client.get(
            "/admin/reservations/maintenancereservations/"
        )
        assert response.status_code == 200
        assert b"Solicitante Admin" in response.content

    def test_create_via_post(self, unit, maintenance_type):
        response = self.client.post(
            "/admin/reservations/maintenancereservations/add/",
            _payload(unit, maintenance_type),
        )
        assert response.status_code == 302
        maintenance = MaintenanceReservations.objects.get(
            applicant="Solicitante Admin"
        )
        assert maintenance.status == MaintenanceReservations.Status.AGENDAMENTO
        assert maintenance.created_by == self.user
        assert maintenance.updated_by == self.user

    def test_create_ignores_forged_status(self, unit, maintenance_type):
        payload = _payload(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        response = self.client.post(
            "/admin/reservations/maintenancereservations/add/", payload
        )
        assert response.status_code == 302
        maintenance = MaintenanceReservations.objects.get(
            applicant="Solicitante Admin"
        )
        assert maintenance.status == MaintenanceReservations.Status.AGENDAMENTO

    def test_create_rejects_end_before_start(self, unit, maintenance_type):
        response = self.client.post(
            "/admin/reservations/maintenancereservations/add/",
            _payload(
                unit,
                maintenance_type,
                startDate="2026-11-15",
                endDate="2026-11-10",
            ),
        )
        assert response.status_code == 200
        assert MaintenanceReservations.objects.count() == 0
        assert "A data final deve ser maior ou igual" in response.content.decode()

    def test_change_page_renders_and_updates_in_agendamento(
        self, unit, maintenance_type
    ):
        maintenance = _factory(unit, maintenance_type)
        change_url = (
            "/admin/reservations/maintenancereservations/%s/change/"
            % maintenance.pk
        )
        response = self.client.get(change_url)
        assert response.status_code == 200

        response = self.client.post(
            change_url,
            _payload(
                unit,
                maintenance_type,
                applicant="Solicitante Alterado",
            ),
        )
        assert response.status_code == 302
        maintenance.refresh_from_db()
        assert maintenance.applicant == "Solicitante Alterado"
        assert maintenance.status == MaintenanceReservations.Status.AGENDAMENTO

    def test_change_page_is_read_only_in_execucao(
        self, unit, maintenance_type
    ):
        maintenance = _factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.EXECUCAO,
        )
        response = self.client.get(
            "/admin/reservations/maintenancereservations/%s/change/"
            % maintenance.pk
        )
        assert response.status_code == 200

        response = self.client.post(
            "/admin/reservations/maintenancereservations/%s/change/"
            % maintenance.pk,
            _payload(
                unit,
                maintenance_type,
                applicant="Tentativa indevida",
            ),
        )
        assert response.status_code == 403
        maintenance.refresh_from_db()
        assert maintenance.applicant == "Solicitante Admin"

    def test_change_page_is_read_only_in_finalizado(
        self, unit, maintenance_type
    ):
        maintenance = _factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        response = self.client.get(
            "/admin/reservations/maintenancereservations/%s/change/"
            % maintenance.pk
        )
        assert response.status_code == 200

        response = self.client.post(
            "/admin/reservations/maintenancereservations/%s/change/"
            % maintenance.pk,
            _payload(
                unit,
                maintenance_type,
                applicant="Tentativa indevida",
            ),
        )
        assert response.status_code == 403
        maintenance.refresh_from_db()
        assert maintenance.applicant == "Solicitante Admin"

    def test_delete_page_allowed_in_finalizado(
        self, unit, maintenance_type
    ):
        maintenance = _factory(
            unit,
            maintenance_type,
            status=MaintenanceReservations.Status.FINALIZADO,
        )
        delete_url = (
            "/admin/reservations/maintenancereservations/%s/delete/"
            % maintenance.pk
        )
        response = self.client.get(delete_url)
        assert response.status_code == 200

        response = self.client.post(delete_url, {"post": "Sim"})
        assert response.status_code == 302
        assert not MaintenanceReservations.objects.filter(
            pk=maintenance.pk
        ).exists()
