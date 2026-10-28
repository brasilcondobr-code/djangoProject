from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from domains.reservations.admin import RentalsAdmin
from domains.reservations.forms import RentalsForm
from domains.reservations.models import Rentals

pytestmark = pytest.mark.django_db


def _admin():
    return RentalsAdmin(Rentals, AdminSite())


def _request(factory, user):
    request = factory.post("/admin/reservations/rentals/")
    request.user = user
    setattr(request, "session", "session")
    setattr(request, "_messages", FallbackStorage(request))
    return request


def _messages(request):
    return [m.message for m in request._messages]


def _payload(unit, rental_type, **overrides):
    data = {
        "condominium": str(unit.pk),
        "typesOfRentals": str(rental_type.pk),
        "startDate": "2026-11-10",
        "endDate": "2026-11-15",
        "applicant": "Solicitante Admin",
        "rentalPrice": "150,00",
        "charge_amount": "True",
        "observations": "",
        "is_active": "on",
        "_save": "Salvar",
    }
    data.update(overrides)
    return data


class TestRentalsAdminConfig:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = RentalsAdmin(Rentals, self.site)
        self.factory = RequestFactory()

    def test_registered(self):
        assert global_admin.site.is_registered(Rentals)
        assert isinstance(
            global_admin.site._registry[Rentals], RentalsAdmin
        )

    def test_form(self):
        assert self.admin.form == RentalsForm

    def test_fieldsets(self):
        principal = self.admin.fieldsets[0]
        assert str(principal[0]) == "Principal"
        assert principal[1]["fields"] == (
            "condominium",
            "typesOfRentals",
            "startDate",
            "endDate",
            "applicant",
            "rentalPrice",
            "charge_amount",
            "observations",
        )

        auditoria = self.admin.fieldsets[-1]
        assert str(auditoria[0]) == "Auditoria"
        assert auditoria[1]["fields"] == (
            "is_active",
            "status",
            "errorStatus",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        assert "collapse" in auditoria[1]["classes"]

    def test_jazzmin_section_order(self):
        assert self.admin.jazzmin_section_order == ["Principal", "Auditoria"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == (
            "status",
            "errorStatus",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def test_list_config(self):
        assert self.admin.list_display == (
            "id",
            "condominium",
            "typesOfRentals",
            "startDate",
            "endDate",
            "applicant",
            "rentalPrice",
            "charge_amount",
            "status",
            "is_active",
        )
        assert self.admin.list_filter == (
            "typesOfRentals",
            "status",
            "charge_amount",
            "is_active",
            "condominium__condominium",
        )
        assert self.admin.autocomplete_fields == (
            "condominium",
            "typesOfRentals",
        )
        assert self.admin.date_hierarchy == "startDate"
        assert self.admin.ordering == ("-startDate", "-id")
        assert self.admin.list_per_page == 25

    def test_actions(self):
        assert self.admin.actions == (
            "reservar_locacoes",
            "finalizar_locacoes",
        )
        assert self.admin.reservar_locacoes.short_description == (
            "Reservar locações selecionadas"
        )
        assert self.admin.finalizar_locacoes.short_description == (
            "Finalizar locações selecionadas"
        )
        assert self.admin.reservar_locacoes.allowed_permissions == ("change",)
        assert self.admin.finalizar_locacoes.allowed_permissions == ("change",)

    def test_media(self):
        assert "js/utils.js" in self.admin.Media.js
        assert "js/rentals_admin.js" in self.admin.Media.js

    def test_admin_js_uses_project_utils(self):
        js_path = (
            Path(__file__).resolve().parents[1]
            / "static"
            / "js"
            / "rentals_admin.js"
        )
        content = js_path.read_text(encoding="utf-8")
        assert "django.jQuery" in content
        assert "BrasilCondoUtils.masks.decimal" in content
        assert "setCustomValidity" in content
        assert "window.BrasilCondoUtils" not in content

    def test_get_queryset_optimized(self):
        request = self.factory.get("/admin/reservations/rentals/")
        request.user = None
        queryset = self.admin.get_queryset(request)
        assert "condominium" in queryset.query.select_related
        assert "typesOfRentals" in queryset.query.select_related
        assert "created_by" in queryset.query.select_related


class TestRentalsAdminPermissions:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.admin = _admin()
        self.factory = RequestFactory()

    def _request(self, user):
        request = self.factory.get("/admin/reservations/rentals/")
        request.user = user
        return request

    def test_change_permission_without_object(self, admin_user):
        assert self.admin.has_change_permission(
            self._request(admin_user)
        ) is True

    def test_change_permission_for_agendamento(
        self, rental_factory, admin_user
    ):
        rental = rental_factory()
        assert self.admin.has_change_permission(
            self._request(admin_user), rental
        ) is True

    @pytest.mark.parametrize(
        "status",
        [Rentals.Status.RESERVADO, Rentals.Status.FINALIZADO],
    )
    def test_change_permission_blocked_for_locked_status(
        self, rental_factory, admin_user, status
    ):
        rental = rental_factory(status=status)
        assert self.admin.has_change_permission(
            self._request(admin_user), rental
        ) is False

    def test_readonly_fields_for_agendamento(
        self, rental_factory, admin_user
    ):
        rental = rental_factory()
        readonly = self.admin.get_readonly_fields(
            self._request(admin_user), rental
        )
        assert set(readonly) == {
            "status",
            "errorStatus",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        }

    @pytest.mark.parametrize(
        "status",
        [Rentals.Status.RESERVADO, Rentals.Status.FINALIZADO],
    )
    def test_all_fields_readonly_for_locked_status(
        self, rental_factory, admin_user, status
    ):
        rental = rental_factory(status=status)
        readonly = self.admin.get_readonly_fields(
            self._request(admin_user), rental
        )
        assert set(readonly) == {
            field.name for field in Rentals._meta.fields
        }


class TestRentalsAdminSaveModel:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.admin = _admin()
        self.factory = RequestFactory()

    def test_create_sets_status_and_audit(
        self, unit, rental_type, admin_user
    ):
        request = _request(self.factory, admin_user)
        rental = Rentals(
            condominium=unit,
            typesOfRentals=rental_type,
            startDate=date(2026, 4, 1),
            endDate=date(2026, 4, 5),
            applicant="  Novo Admin  ",
            rentalPrice=Decimal("80.00"),
            charge_amount=True,
            status=Rentals.Status.FINALIZADO,
        )

        self.admin.save_model(request, rental, form=None, change=False)

        rental.refresh_from_db()
        assert rental.status == Rentals.Status.AGENDAMENTO
        assert rental.created_by == admin_user
        assert rental.updated_by == admin_user
        assert rental.applicant == "Novo Admin"
        assert rental.errorStatus == ""

    def test_update_preserves_created_by_and_sets_updated_by(
        self, rental_factory, admin_user, other_user
    ):
        rental = rental_factory(
            created_by=admin_user, updated_by=admin_user
        )
        request = _request(self.factory, other_user)
        rental.applicant = "Editado pelo Admin"

        self.admin.save_model(request, rental, form=None, change=True)

        rental.refresh_from_db()
        assert rental.created_by == admin_user
        assert rental.updated_by == other_user
        assert rental.applicant == "Editado pelo Admin"


class TestRentalsAdminActions:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.admin = _admin()
        self.factory = RequestFactory()

    def test_reservar_action_success_and_rejection(
        self, rental_factory, admin_user
    ):
        eligible = rental_factory()
        finalized = rental_factory(status=Rentals.Status.FINALIZADO)
        request = _request(self.factory, admin_user)
        queryset = Rentals.objects.filter(pk__in=[eligible.pk, finalized.pk])

        self.admin.reservar_locacoes(request, queryset)

        eligible.refresh_from_db()
        finalized.refresh_from_db()
        assert eligible.status == Rentals.Status.RESERVADO
        assert finalized.status == Rentals.Status.FINALIZADO
        assert finalized.errorStatus

        messages = _messages(request)
        assert any("1 locação(ões) reservada(s)" in m for m in messages)
        assert any(f"#{eligible.pk}" in m for m in messages)
        assert any("1 locação(ões) rejeitada(s)" in m for m in messages)
        assert any(
            f"#{finalized.pk}:" in m for m in messages
        )

    def test_finalizar_action_success(self, rental_factory, admin_user):
        rental = rental_factory(status=Rentals.Status.RESERVADO)
        request = _request(self.factory, admin_user)

        self.admin.finalizar_locacoes(
            request, Rentals.objects.filter(pk=rental.pk)
        )

        rental.refresh_from_db()
        assert rental.status == Rentals.Status.FINALIZADO
        assert any(
            "1 locação(ões) finalizada(s)" in m
            for m in _messages(request)
        )

    def test_action_without_records_reports_warning(
        self, admin_user
    ):
        request = _request(self.factory, admin_user)
        self.admin.reservar_locacoes(request, Rentals.objects.none())
        assert any(
            "Nenhuma locação selecionada." in m
            for m in _messages(request)
        )


class TestRentalsAdminIntegration:

    def _login(self, client, admin_user):
        assert client.login(username="admin", password="admin123")

    def test_add_page_renders(self, client, admin_user, unit, rental_type):
        self._login(client, admin_user)
        response = client.get("/admin/reservations/rentals/add/")
        assert response.status_code == 200
        content = response.content.decode()

        for field_id in (
            "id_condominium",
            "id_typesOfRentals",
            "id_startDate",
            "id_endDate",
            "id_applicant",
            "id_rentalPrice",
            "id_charge_amount",
            "id_observations",
        ):
            assert 'id="%s"' % field_id in content

        assert "Sim<" in content
        assert "Não<" in content
        assert 'id="id_status"' not in content
        assert "js/rentals_admin.js" in content

        start_line = next(
            line
            for line in content.splitlines()
            if 'id="id_startDate"' in line
        )
        assert 'type="date"' in start_line

    def test_create_via_post(
        self, client, admin_user, unit, rental_type
    ):
        self._login(client, admin_user)
        payload = _payload(
            unit,
            rental_type,
            status=Rentals.Status.FINALIZADO,
            created_by="",
            updated_by="",
        )
        response = client.post(
            "/admin/reservations/rentals/add/", payload
        )

        assert response.status_code == 302
        rental = Rentals.objects.get()
        assert rental.status == Rentals.Status.AGENDAMENTO
        assert rental.created_by == admin_user
        assert rental.updated_by == admin_user
        assert rental.rentalPrice == Decimal("150.00")
        assert rental.startDate == date(2026, 11, 10)
        assert rental.endDate == date(2026, 11, 15)

    def test_create_without_charge_clears_price(
        self, client, admin_user, unit, rental_type
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/reservations/rentals/add/",
            _payload(
                unit,
                rental_type,
                charge_amount="False",
                rentalPrice="999,00",
            ),
        )

        assert response.status_code == 302
        assert Rentals.objects.get().rentalPrice is None

    def test_create_rejects_end_before_start(
        self, client, admin_user, unit, rental_type
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/reservations/rentals/add/",
            _payload(
                unit,
                rental_type,
                startDate="2026-11-20",
                endDate="2026-11-10",
            ),
        )

        assert response.status_code == 200
        assert response.context["adminform"].form.errors
        assert Rentals.objects.count() == 0

    def test_create_rejects_when_capacity_is_reached(
        self, client, admin_user, unit, rental_type, rental_factory
    ):
        rental_type.numberOfAppointments = 1
        rental_type.save(update_fields=["numberOfAppointments"])
        rental_factory(
            startDate=date(2026, 11, 10),
            endDate=date(2026, 11, 15),
        )
        self._login(client, admin_user)

        response = client.post(
            "/admin/reservations/rentals/add/",
            _payload(unit, rental_type),
        )

        assert response.status_code == 200
        assert "Limite de 1 agendamento" in response.content.decode()
        assert Rentals.objects.count() == 1

    def test_edit_agendamento_via_post(
        self, client, admin_user, other_user, rental_factory
    ):
        rental = rental_factory(
            created_by=admin_user, updated_by=admin_user
        )
        self._login(client, admin_user)
        response = client.post(
            f"/admin/reservations/rentals/{rental.pk}/change/",
            _payload(
                rental.condominium,
                rental.typesOfRentals,
                applicant="Alterado via Admin",
                startDate="2026-01-12",
                endDate="2026-01-16",
            ),
        )

        assert response.status_code == 302
        rental.refresh_from_db()
        assert rental.applicant == "Alterado via Admin"
        assert rental.created_by == admin_user
        assert rental.updated_by == admin_user

    def test_edit_without_charge_clears_price_even_if_field_is_absent(
        self, client, admin_user, rental_factory
    ):
        rental = rental_factory(rentalPrice=Decimal("100.00"))
        self._login(client, admin_user)
        payload = _payload(
            rental.condominium,
            rental.typesOfRentals,
            charge_amount="False",
            startDate="2026-01-10",
            endDate="2026-01-15",
        )
        payload.pop("rentalPrice")

        response = client.post(
            f"/admin/reservations/rentals/{rental.pk}/change/", payload
        )

        assert response.status_code == 302
        rental.refresh_from_db()
        assert rental.charge_amount is False
        assert rental.rentalPrice is None

    @pytest.mark.parametrize(
        "status",
        [Rentals.Status.RESERVADO, Rentals.Status.FINALIZADO],
    )
    def test_manipulated_post_cannot_edit_locked_status(
        self, client, admin_user, rental_factory, status
    ):
        rental = rental_factory(status=status)
        original_applicant = rental.applicant
        self._login(client, admin_user)

        response = client.post(
            f"/admin/reservations/rentals/{rental.pk}/change/",
            _payload(
                rental.condominium,
                rental.typesOfRentals,
                applicant="Tentativa indevida",
            ),
        )

        assert response.status_code == 403
        rental.refresh_from_db()
        assert rental.applicant == original_applicant
        assert rental.status == status

    @pytest.mark.parametrize(
        "status",
        [Rentals.Status.RESERVADO, Rentals.Status.FINALIZADO],
    )
    def test_change_page_is_read_only_for_locked_status(
        self, client, admin_user, rental_factory, status
    ):
        rental = rental_factory(status=status)
        self._login(client, admin_user)

        response = client.get(
            f"/admin/reservations/rentals/{rental.pk}/change/"
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert rental.applicant in content
        # Campos somente leitura não são renderizados como inputs editáveis.
        assert 'name="applicant"' not in content
        assert 'name="startDate"' not in content

