from datetime import date
from decimal import Decimal

import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.urls import reverse

from domains.financial.admin import NewReleaseAdmin, ScopeMonthFilter
from domains.financial.forms import NewReleaseForm
from domains.financial.models import NewRelease


@pytest.mark.django_db
class TestNewReleaseAdminConfiguration:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.model_admin = NewReleaseAdmin(NewRelease, self.site)
        self.factory = RequestFactory()

    def _request(self, user):
        request = self.factory.get("/admin/")
        request.user = user
        return request

    def test_registered_in_default_admin_site(self):
        assert admin.site._registry[NewRelease] is not None

    def test_form(self):
        assert self.model_admin.form is NewReleaseForm

    def test_list_display(self):
        assert self.model_admin.list_display == (
            "id",
            "condominium",
            "paymaster",
            "title",
            "scope_display",
            "launchDate",
            "chartOfAccounts",
            "fund",
            "launch_type_display",
            "value_display",
            "status_display",
            "is_active",
        )

    def test_list_filter(self):
        assert self.model_admin.list_filter == (
            "status",
            ScopeMonthFilter,
            "launchType",
            "is_active",
            "condominium__condominium",
            "fund",
            "chartOfAccounts",
        )

    def test_search_fields(self):
        assert "title" in self.model_admin.search_fields
        assert "paymaster__name" in self.model_admin.search_fields
        assert "condominium__condominium__name" in (
            self.model_admin.search_fields
        )

    def test_autocomplete_fields(self):
        assert self.model_admin.autocomplete_fields == (
            "condominium",
            "chartOfAccounts",
            "fund",
        )

    def test_readonly_fields(self):
        assert self.model_admin.readonly_fields == (
            "status_display",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def test_fieldsets_have_principal_and_auditoria_tabs(self):
        names = [fieldset[0] for fieldset in self.model_admin.fieldsets]
        assert names == ["Principal", "Auditoria"]

        principal = self.model_admin.fieldsets[0][1]["fields"]
        auditoria = self.model_admin.fieldsets[1][1]["fields"]
        assert "paymaster" in principal
        assert "launchType" in principal
        assert "value" in principal
        assert principal.index("launchDate") < principal.index("scope")
        assert principal.index("scope") < principal.index("title")
        assert "status_display" in auditoria
        assert "created_by" in auditoria
        assert "updated_by" in auditoria

    def test_actions(self):
        assert self.model_admin.actions == (
            "gerar_cobranca",
            "excluir_lancamentos",
        )

    def test_delete_selected_is_removed(self, _user):
        actions = self.model_admin.get_actions(self._request(_user))
        assert "delete_selected" not in actions
        assert "gerar_cobranca" in actions
        assert "excluir_lancamentos" in actions

    def test_ajax_url_is_registered(self):
        urls = self.model_admin.get_urls()
        names = {url.name for url in urls if getattr(url, "name", None)}
        assert "financial_newrelease_residents_by_unit" in names

    def test_scope_display(self, _new_release):
        assert self.model_admin.scope_display(_new_release) == "Janeiro/2026"

    def test_scope_display_without_scope(self):
        assert self.model_admin.scope_display(NewRelease()) == "-"

    def test_launch_type_display(self, _new_release):
        assert self.model_admin.launch_type_display(_new_release) == "Débito"

    def test_value_display(self, _new_release):
        assert self.model_admin.value_display(_new_release) == "-150,00"

    def test_value_display_without_value(self):
        assert self.model_admin.value_display(NewRelease()) == "-"

    def test_status_display(self, _new_release):
        assert self.model_admin.status_display(_new_release) == "Lançamento"
        assert self.model_admin.status_display() == "Lançamento"


@pytest.mark.django_db
class TestScopeMonthFilter:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.model_admin = NewReleaseAdmin(NewRelease, self.site)
        self.factory = RequestFactory()

    def _filter(self, value=None):
        params = {} if value is None else {"scope": [value]}
        return ScopeMonthFilter(
            self.factory.get("/admin/"),
            params,
            NewRelease,
            self.model_admin,
        )

    def test_title_and_parameter(self):
        scope_filter = self._filter()

        assert scope_filter.title == "Competência"
        assert scope_filter.parameter_name == "scope"

    def test_lookups_use_month_year_format(
        self, _new_release, _billing_release
    ):
        lookups = self._filter().lookups(
            self.factory.get("/admin/"), self.model_admin
        )

        assert lookups == (("02-2026", "02-2026"), ("01-2026", "01-2026"))

    def test_queryset_filters_selected_competence(
        self, _new_release, _billing_release
    ):
        filtered = self._filter("01-2026").queryset(
            self.factory.get("/admin/"), NewRelease.objects.all()
        )

        assert set(filtered.values_list("pk", flat=True)) == {
            _new_release.pk
        }

    def test_queryset_ignores_invalid_value(self, _new_release):
        filtered = self._filter("invalido").queryset(
            self.factory.get("/admin/"), NewRelease.objects.all()
        )

        assert _new_release in filtered


@pytest.mark.django_db
class TestNewReleaseAdminPermissions:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.model_admin = NewReleaseAdmin(NewRelease, self.site)
        self.factory = RequestFactory()

    def _request(self, user):
        request = self.factory.get("/admin/")
        request.user = user
        return request

    def test_lancamento_can_be_changed(self, _user, _new_release):
        request = self._request(_user)
        assert self.model_admin.has_change_permission(
            request, _new_release
        ) is True

    def test_cobranca_cannot_be_changed(self, _user, _billing_release):
        request = self._request(_user)
        assert self.model_admin.has_change_permission(
            request, _billing_release
        ) is False

    def test_lancamento_can_be_deleted(self, _user, _new_release):
        request = self._request(_user)
        assert self.model_admin.has_delete_permission(
            request, _new_release
        ) is True

    def test_cobranca_cannot_be_deleted(self, _user, _billing_release):
        request = self._request(_user)
        assert self.model_admin.has_delete_permission(
            request, _billing_release
        ) is False

    def test_readonly_fields_for_cobranca(
        self, _user, _billing_release
    ):
        request = self._request(_user)
        readonly = self.model_admin.get_readonly_fields(
            request, _billing_release
        )
        assert "status_display" in readonly
        assert "title" in readonly
        assert "value" in readonly
        assert "condominium" in readonly
        assert "paymaster" in readonly
        assert "status" in readonly

    def test_readonly_fields_for_lancamento(
        self, _user, _new_release
    ):
        request = self._request(_user)
        readonly = self.model_admin.get_readonly_fields(
            request, _new_release
        )
        assert readonly == [
            "status_display",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def test_staff_without_permission_cannot_change(
        self, _staff_user, _new_release
    ):
        request = self._request(_staff_user)
        assert self.model_admin.has_change_permission(
            request, _new_release
        ) is False


@pytest.mark.django_db
class TestNewReleaseAdminAjax:

    def test_returns_residents_of_the_selected_unit(
        self,
        _client,
        _user,
        _unit,
        _resident,
        _resident_two,
        _resident_inactive,
    ):
        _client.force_login(_user)

        response = _client.get(
            reverse("admin:financial_newrelease_residents_by_unit"),
            {"unit_id": _unit.pk},
        )

        assert response.status_code == 200
        payload = response.json()
        ids = {item["id"] for item in payload["results"]}
        assert ids == {_resident.pk}
        assert _resident_two.pk not in ids
        assert _resident_inactive.pk not in ids
        assert payload["results"] == [
            {
                "id": _resident.pk,
                "text": "Morador Um | Morador(a) | Condomínio Teste - A - 101",
            }
        ]

    def test_missing_unit_returns_400(self, _client, _user):
        _client.force_login(_user)

        response = _client.get(
            reverse("admin:financial_newrelease_residents_by_unit")
        )

        assert response.status_code == 400
        assert response.json()["results"] == []

    def test_invalid_unit_returns_400(self, _client, _user):
        _client.force_login(_user)

        response = _client.get(
            reverse("admin:financial_newrelease_residents_by_unit"),
            {"unit_id": "abc"},
        )

        assert response.status_code == 400

    def test_requires_staff_permission(self, _client, _staff_user, _unit):
        _client.force_login(_staff_user)

        response = _client.get(
            reverse("admin:financial_newrelease_residents_by_unit"),
            {"unit_id": _unit.pk},
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestNewReleaseAdminIntegration:

    def _payload(
        self, unit, resident, chart_account, fund, **overrides
    ):
        payload = {
            "condominium": unit.pk,
            "paymaster": resident.pk,
            "title": "Lançamento via Admin",
            "scope": "07-2026",
            "launchDate": "2026-07-10",
            "chartOfAccounts": chart_account.pk,
            "fund": fund.pk,
            "launchType": NewRelease.LaunchType.DEBITO,
            "value": "1.234,56",
            "notes": "",
            "is_active": "on",
            "_save": "Salvar",
        }
        payload.update(overrides)
        return payload

    def test_changelist_renders(self, _client, _user, _new_release):
        _client.force_login(_user)

        response = _client.get(
            reverse("admin:financial_newrelease_changelist")
        )

        assert response.status_code == 200

    def test_add_page_renders(self, _client, _user):
        from django.utils import timezone

        _client.force_login(_user)

        response = _client.get(
            reverse("admin:financial_newrelease_add")
        )

        assert response.status_code == 200
        content = response.content.decode()
        expected_title = (
            "Taxa condominial de: "
            f"{timezone.localdate().strftime('%m-%Y')}"
        )
        assert f'value="{expected_title}"' in content
        assert "newrelease_admin.js" in content
        assert "css/newrelease_admin.css" in content

    def test_add_page_uses_autocomplete_for_related_fields(
        self, _client, _user
    ):
        from django.contrib.admin.widgets import AutocompleteSelect

        _client.force_login(_user)
        response = _client.get(
            reverse("admin:financial_newrelease_add")
        )
        form = response.context["adminform"].form

        for name in ("condominium", "chartOfAccounts", "fund"):
            widget = form.fields[name].widget
            while hasattr(widget, "widget"):
                widget = widget.widget
            assert isinstance(widget, AutocompleteSelect)

    def test_change_page_renders(self, _client, _user, _new_release):
        _client.force_login(_user)

        response = _client.get(
            reverse(
                "admin:financial_newrelease_change",
                args=[_new_release.pk],
            )
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="scope"' in content
        assert 'value="01-2026"' in content
        assert "newrelease_admin.js" in content

    def test_add_sets_status_and_audit(
        self,
        _client,
        _user,
        _unit,
        _resident,
        _chart_account,
        _fund,
    ):
        _client.force_login(_user)

        response = _client.post(
            reverse("admin:financial_newrelease_add"),
            self._payload(_unit, _resident, _chart_account, _fund),
        )

        assert response.status_code == 302, response.content
        release = NewRelease.objects.get(title="Lançamento via Admin")
        assert release.status == NewRelease.Status.LANCAMENTO
        assert release.created_by == _user
        assert release.updated_by == _user
        assert release.scope == date(2026, 7, 1)
        assert release.value == Decimal("-1234.56")

    def test_add_rejects_paymaster_of_another_unit(
        self,
        _client,
        _user,
        _unit,
        _resident_two,
        _chart_account,
        _fund,
    ):
        _client.force_login(_user)

        response = _client.post(
            reverse("admin:financial_newrelease_add"),
            self._payload(
                _unit, _resident_two, _chart_account, _fund
            ),
        )

        assert response.status_code == 200
        assert not NewRelease.objects.filter(
            title="Lançamento via Admin"
        ).exists()
        assert "paymaster" in response.context["adminform"].form.errors

    def test_change_lancamento(
        self,
        _client,
        _user,
        _new_release,
        _unit,
        _resident,
        _chart_account,
        _fund,
    ):
        _client.force_login(_user)
        created_by = _new_release.created_by_id

        response = _client.post(
            reverse(
                "admin:financial_newrelease_change",
                args=[_new_release.pk],
            ),
            self._payload(
                _unit,
                _resident,
                _chart_account,
                _fund,
                title="Título Alterado",
                scope="01-2026",
                launchDate="2026-01-10",
                value="200,00",
            ),
        )

        assert response.status_code == 302, response.content
        _new_release.refresh_from_db()
        assert _new_release.title == "Título Alterado"
        assert _new_release.value == Decimal("-200.00")
        assert _new_release.created_by_id == created_by
        assert _new_release.updated_by == _user

    def test_change_cobranca_is_forbidden(
        self,
        _client,
        _user,
        _billing_release,
        _unit,
        _resident,
        _chart_account,
        _fund,
    ):
        _client.force_login(_user)

        response = _client.post(
            reverse(
                "admin:financial_newrelease_change",
                args=[_billing_release.pk],
            ),
            self._payload(
                _unit,
                _resident,
                _chart_account,
                _fund,
                title="Tentativa",
                scope="02-2026",
                launchDate="2026-02-10",
            ),
        )

        assert response.status_code == 403
        _billing_release.refresh_from_db()
        assert _billing_release.title == "Lançamento Cobrado"

    def test_delete_cobranca_is_forbidden(
        self, _client, _user, _billing_release
    ):
        _client.force_login(_user)

        response = _client.post(
            reverse(
                "admin:financial_newrelease_delete",
                args=[_billing_release.pk],
            ),
            {"post": "yes"},
        )

        assert response.status_code == 403
        assert NewRelease.objects.filter(
            pk=_billing_release.pk
        ).exists()

    def test_delete_lancamento(
        self, _client, _user, _new_release
    ):
        _client.force_login(_user)
        pk = _new_release.pk

        response = _client.post(
            reverse("admin:financial_newrelease_delete", args=[pk]),
            {"post": "yes"},
        )

        assert response.status_code == 302
        assert not NewRelease.objects.filter(pk=pk).exists()

    def test_action_generate_billing(
        self, _client, _user, _new_release
    ):
        _client.force_login(_user)

        response = _client.post(
            reverse("admin:financial_newrelease_changelist"),
            {
                "action": "gerar_cobranca",
                "_selected_action": [str(_new_release.pk)],
                "select_across": "0",
                "index": "0",
            },
            follow=True,
        )

        assert response.status_code == 200
        _new_release.refresh_from_db()
        assert _new_release.status == NewRelease.Status.COBRANCA
        assert _new_release.updated_by == _user

    def test_action_generate_billing_reports_blocked_items(
        self,
        _client,
        _user,
        _new_release,
        _billing_release,
    ):
        _client.force_login(_user)

        response = _client.post(
            reverse("admin:financial_newrelease_changelist"),
            {
                "action": "gerar_cobranca",
                "_selected_action": [
                    str(_new_release.pk),
                    str(_billing_release.pk),
                ],
                "select_across": "0",
                "index": "0",
            },
            follow=True,
        )

        assert response.status_code == 200
        messages = [
            str(message) for message in response.context["messages"]
        ]
        assert any("cobrança gerada" in message for message in messages)
        assert any(
            f"ID {_billing_release.pk}" in message
            for message in messages
        )
        _new_release.refresh_from_db()
        assert _new_release.status == NewRelease.Status.COBRANCA

    def test_action_delete_lancamentos(
        self, _client, _user, _new_release
    ):
        _client.force_login(_user)
        pk = _new_release.pk

        response = _client.post(
            reverse("admin:financial_newrelease_changelist"),
            {
                "action": "excluir_lancamentos",
                "_selected_action": [str(pk)],
                "select_across": "0",
                "index": "0",
            },
            follow=True,
        )

        assert response.status_code == 200
        assert not NewRelease.objects.filter(pk=pk).exists()

    def test_action_delete_keeps_billing_items(
        self,
        _client,
        _user,
        _new_release,
        _billing_release,
    ):
        _client.force_login(_user)

        response = _client.post(
            reverse("admin:financial_newrelease_changelist"),
            {
                "action": "excluir_lancamentos",
                "_selected_action": [
                    str(_new_release.pk),
                    str(_billing_release.pk),
                ],
                "select_across": "0",
                "index": "0",
            },
            follow=True,
        )

        assert response.status_code == 200
        messages = [
            str(message) for message in response.context["messages"]
        ]
        assert any("excluído" in message for message in messages)
        assert any(
            f"ID {_billing_release.pk}" in message
            for message in messages
        )
        assert not NewRelease.objects.filter(
            pk=_new_release.pk
        ).exists()
        assert NewRelease.objects.filter(
            pk=_billing_release.pk
        ).exists()
