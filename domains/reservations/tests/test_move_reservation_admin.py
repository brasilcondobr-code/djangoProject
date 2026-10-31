from datetime import date

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from domains.reservations.admin import MoveReservationsAdmin
from domains.reservations.forms import MoveReservationsForm
from domains.reservations.models import MoveReservations

pytestmark = pytest.mark.django_db


def _admin():
    return MoveReservationsAdmin(MoveReservations, AdminSite())


def _request(factory, user):
    request = factory.post("/admin/reservations/movereservations/")
    request.user = user
    setattr(request, "session", "session")
    setattr(request, "_messages", FallbackStorage(request))
    return request


def _messages(request):
    return [m.message for m in request._messages]


def _payload(unit, **overrides):
    data = {
        "condominium": str(unit.pk),
        "typeOfChange": "E",
        "startDate": "2026-11-10",
        "endDate": "2026-11-15",
        "applicant": "Solicitante Admin",
        "observations": "",
        "is_active": "on",
        "_save": "Salvar",
    }
    data.update(overrides)
    return data


def _factory(unit, **overrides):
    data = {
        "condominium": unit,
        "typeOfChange": "E",
        "startDate": date(2026, 11, 10),
        "endDate": date(2026, 11, 15),
        "applicant": "Solicitante Admin",
    }
    data.update(overrides)
    return MoveReservations.objects.create(**data)


class TestMoveReservationsAdminConfig:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = MoveReservationsAdmin(MoveReservations, self.site)
        self.factory = RequestFactory()

    def test_registered(self):
        assert global_admin.site.is_registered(MoveReservations)

    def test_admin_form(self):
        assert self.admin.form == MoveReservationsForm

    def test_list_display(self):
        assert self.admin.list_display == (
            "id",
            "condominium",
            "typeOfChange",
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
            "typeOfChange",
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
            "typeOfChange",
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
            "executar_mudancas",
            "finalizar_mudancas",
        )

    def test_action_descriptions(self):
        assert (
            self.admin.executar_mudancas.short_description
            == "Executar mudanças selecionadas"
        )
        assert (
            self.admin.finalizar_mudancas.short_description
            == "Finalizar mudanças selecionadas"
        )

    def test_media_includes_date_script(self):
        assert "js/move_reservations_admin.js" in str(self.admin.media)

    def test_change_permission_only_agendamento(self, unit, admin_user):
        admin = _admin()
        request = _request(self.factory, admin_user)
        agendamento = _factory(unit)
        execucao = _factory(
            unit, status=MoveReservations.Status.EXECUCAO
        )
        finalizado = _factory(
            unit, status=MoveReservations.Status.FINALIZADO
        )
        assert admin.has_change_permission(request, agendamento) is True
        assert admin.has_change_permission(request, execucao) is False
        assert admin.has_change_permission(request, finalizado) is False

    def test_readonly_all_fields_outside_agendamento(self, unit, admin_user):
        admin = _admin()
        request = _request(self.factory, admin_user)
        agendamento = _factory(unit)
        execucao = _factory(
            unit, status=MoveReservations.Status.EXECUCAO
        )

        assert admin.get_readonly_fields(request, agendamento) == [
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        assert set(admin.get_readonly_fields(request, execucao)) == {
            field.name for field in MoveReservations._meta.fields
        }

    def test_save_model_new_sets_server_status_and_audit(
        self, unit, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        move = MoveReservations(
            condominium=unit,
            typeOfChange="E",
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 15),
            applicant="Solicitante Admin",
            status=MoveReservations.Status.FINALIZADO,
        )
        admin.save_model(request, move, form=None, change=False)

        assert move.pk is not None
        assert move.status == MoveReservations.Status.AGENDAMENTO
        assert move.created_by == admin_user
        assert move.updated_by == admin_user

    def test_execute_action_reports_success_and_failure(
        self, unit, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        agendada = _factory(unit)
        finalizada = _factory(
            unit, status=MoveReservations.Status.FINALIZADO
        )

        queryset = MoveReservations.objects.filter(
            pk__in=[agendada.pk, finalizada.pk]
        )
        admin.executar_mudancas(request, queryset)

        agendada.refresh_from_db()
        assert agendada.status == MoveReservations.Status.EXECUCAO
        messages = _messages(request)
        assert any("1 mudança(s) executada(s) com sucesso" in m for m in messages)
        assert any(f"#{finalizada.pk}:" in m for m in messages)

    def test_finalize_action_reports_success_and_failure(
        self, unit, admin_user
    ):
        admin = _admin()
        request = _request(self.factory, admin_user)
        em_execucao = _factory(
            unit, status=MoveReservations.Status.EXECUCAO
        )
        agendada = _factory(unit)

        queryset = MoveReservations.objects.filter(
            pk__in=[em_execucao.pk, agendada.pk]
        )
        admin.finalizar_mudancas(request, queryset)

        em_execucao.refresh_from_db()
        assert em_execucao.status == MoveReservations.Status.FINALIZADO
        messages = _messages(request)
        assert any("1 mudança(s) finalizada(s) com sucesso" in m for m in messages)
        assert any(f"#{agendada.pk}:" in m for m in messages)

    def test_action_with_empty_queryset_reports_nothing(self, admin_user):
        admin = _admin()
        request = _request(self.factory, admin_user)
        admin.executar_mudancas(request, MoveReservations.objects.none())
        assert "Nenhuma mudança selecionada." in _messages(request)


class TestMoveReservationsAdminRender:

    @pytest.fixture(autouse=True)
    def setup(self, client, django_user_model):
        self.client = client
        self.user = django_user_model.objects.create_superuser(
            username="admin_mov", email="admin_mov@teste.com", password="admin123"
        )
        assert self.client.login(username="admin_mov", password="admin123")

    def test_add_page_renders(self):
        response = self.client.get(
            "/admin/reservations/movereservations/add/"
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "Nome do solicitante" in content
        assert "Principal" in content
        assert "Auditoria" in content
        assert "Entrada" in content
        assert "Saída" in content

    def test_changelist_renders(self, unit):
        _factory(unit)
        response = self.client.get(
            "/admin/reservations/movereservations/"
        )
        assert response.status_code == 200
        assert b"Solicitante Admin" in response.content

    def test_create_via_post(self, unit):
        response = self.client.post(
            "/admin/reservations/movereservations/add/",
            _payload(unit),
        )
        assert response.status_code == 302
        move = MoveReservations.objects.get(applicant="Solicitante Admin")
        assert move.status == MoveReservations.Status.AGENDAMENTO
        assert move.created_by == self.user
        assert move.updated_by == self.user

    def test_create_ignores_forged_status(self, unit):
        payload = _payload(
            unit, status=MoveReservations.Status.FINALIZADO
        )
        response = self.client.post(
            "/admin/reservations/movereservations/add/", payload
        )
        assert response.status_code == 302
        move = MoveReservations.objects.get(applicant="Solicitante Admin")
        assert move.status == MoveReservations.Status.AGENDAMENTO

    def test_create_rejects_end_before_start(self, unit):
        response = self.client.post(
            "/admin/reservations/movereservations/add/",
            _payload(
                unit,
                startDate="2026-11-15",
                endDate="2026-11-10",
            ),
        )
        assert response.status_code == 200
        assert MoveReservations.objects.count() == 0
        assert "A data final deve ser maior ou igual" in response.content.decode()

    def test_create_rejects_invalid_type(self, unit):
        response = self.client.post(
            "/admin/reservations/movereservations/add/",
            _payload(unit, typeOfChange="X"),
        )
        assert response.status_code == 200
        assert MoveReservations.objects.count() == 0

    def test_change_page_renders_and_updates_in_agendamento(self, unit):
        move = _factory(unit)
        change_url = (
            "/admin/reservations/movereservations/%s/change/" % move.pk
        )
        response = self.client.get(change_url)
        assert response.status_code == 200

        response = self.client.post(
            change_url,
            _payload(unit, applicant="Solicitante Alterado"),
        )
        assert response.status_code == 302
        move.refresh_from_db()
        assert move.applicant == "Solicitante Alterado"
        assert move.status == MoveReservations.Status.AGENDAMENTO

    def test_change_page_is_read_only_in_execucao(self, unit):
        move = _factory(unit, status=MoveReservations.Status.EXECUCAO)
        change_url = (
            "/admin/reservations/movereservations/%s/change/" % move.pk
        )
        response = self.client.get(change_url)
        assert response.status_code == 200

        response = self.client.post(
            change_url,
            _payload(unit, applicant="Tentativa indevida"),
        )
        assert response.status_code == 403
        move.refresh_from_db()
        assert move.applicant == "Solicitante Admin"

    def test_change_page_is_read_only_in_finalizado(self, unit):
        move = _factory(unit, status=MoveReservations.Status.FINALIZADO)
        change_url = (
            "/admin/reservations/movereservations/%s/change/" % move.pk
        )
        response = self.client.get(change_url)
        assert response.status_code == 200

        response = self.client.post(
            change_url,
            _payload(unit, applicant="Tentativa indevida"),
        )
        assert response.status_code == 403
        move.refresh_from_db()
        assert move.applicant == "Solicitante Admin"

    def test_delete_page_allowed_in_finalizado(self, unit):
        move = _factory(unit, status=MoveReservations.Status.FINALIZADO)
        delete_url = (
            "/admin/reservations/movereservations/%s/delete/" % move.pk
        )
        response = self.client.get(delete_url)
        assert response.status_code == 200

        response = self.client.post(delete_url, {"post": "Sim"})
        assert response.status_code == 302
        assert not MoveReservations.objects.filter(pk=move.pk).exists()
