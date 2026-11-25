from datetime import date
from decimal import Decimal

import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

from domains.financial.admin import CollectionAdmin, CollectionCreditInline
from domains.financial.forms import CollectionForm
from domains.financial.models import Collection, Payment


@pytest.mark.django_db
class TestCollectionAdminConfiguration:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.model_admin = CollectionAdmin(Collection, self.site)
        self.factory = RequestFactory()

    def _request(self, user):
        request = self.factory.get("/admin/")
        request.user = user
        return request

    def test_registered_in_default_admin_site(self):
        assert admin.site._registry[Collection] is not None

    def test_form_and_inline(self):
        assert self.model_admin.form is CollectionForm
        assert CollectionCreditInline in self.model_admin.inlines

    def test_list_display(self):
        assert self.model_admin.list_display == (
            "id",
            "condominium",
            "billingDate",
            "scope_display",
            "dueDate",
            "total_display",
            "balance_display",
            "status_display",
            "is_active",
        )

    def test_fieldsets_have_three_sections(self):
        names = [fieldset[0] for fieldset in self.model_admin.fieldsets]

        assert names == ["Principal", "Composição", "Auditoria"]

    def test_jazzmin_section_order(self):
        assert self.model_admin.jazzmin_section_order == (
            "Principal",
            "Composição",
            "Créditos",
            "Auditoria",
        )

    def test_readonly_fields(self):
        readonly = self.model_admin.readonly_fields

        for field in (
            "billingDate",
            "totalAmount",
            "balance",
            "status_display",
            "errorStatus",
            "composition_table",
            "created_by",
            "updated_by",
        ):
            assert field in readonly

    def test_actions(self):
        assert self.model_admin.actions == (
            "atualizar_cobranca",
            "pagamento",
            "excluir_cobrancas",
        )

    def test_delete_selected_is_removed(self, _user):
        actions = self.model_admin.get_actions(self._request(_user))

        assert "delete_selected" not in actions
        assert "atualizar_cobranca" in actions
        assert "pagamento" in actions

    def test_display_methods(self, _collection):
        assert self.model_admin.scope_display(_collection) == "Janeiro/2026"
        assert self.model_admin.total_display(_collection) == "935,00"
        assert self.model_admin.balance_display(_collection) == "935,00"
        assert self.model_admin.status_display(_collection) == "A vencer"
        assert self.model_admin.status_display() == "A vencer"

    def test_display_methods_without_values(self):
        collection = Collection()

        assert self.model_admin.scope_display(collection) == "-"
        assert self.model_admin.total_display(collection) == "-"
        assert self.model_admin.composition_table() == "-"

    def test_composition_table_lists_linked_releases(
        self, _collection, _billing_release
    ):
        _billing_release.collection = _collection
        _billing_release.save(update_fields=["collection"])

        html = self.model_admin.composition_table(_collection)

        assert f"<td>{_billing_release.pk}</td>" in html
        assert "Lançamento Cobrado" in html


@pytest.mark.django_db
class TestCollectionAdminPermissions:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.model_admin = CollectionAdmin(Collection, self.site)
        self.factory = RequestFactory()

    def _request(self, user):
        request = self.factory.get("/admin/")
        request.user = user
        return request

    def test_to_be_won_can_be_changed_and_deleted(
        self, _user, _collection
    ):
        request = self._request(_user)

        assert self.model_admin.has_change_permission(
            request, _collection
        ) is True
        assert self.model_admin.has_delete_permission(
            request, _collection
        ) is True

    def test_expired_cannot_be_changed_or_deleted(
        self, _user, _expired_collection
    ):
        request = self._request(_user)

        assert self.model_admin.has_change_permission(
            request, _expired_collection
        ) is False
        assert self.model_admin.has_delete_permission(
            request, _expired_collection
        ) is False

    def test_inactive_cannot_be_changed_but_can_be_deleted(
        self, _user, _collection
    ):
        _collection.is_active = False
        _collection.save(update_fields=["is_active"])
        request = self._request(_user)

        assert self.model_admin.has_change_permission(
            request, _collection
        ) is False
        assert self.model_admin.has_delete_permission(
            request, _collection
        ) is True

    def test_linked_collection_cannot_be_deleted(
        self, _user, _collection, _billing_release
    ):
        _billing_release.collection = _collection
        _billing_release.save(update_fields=["collection"])
        request = self._request(_user)

        assert self.model_admin.has_delete_permission(
            request, _collection
        ) is False

    def test_staff_without_permission_cannot_change(
        self, _staff_user, _collection
    ):
        request = self._request(_staff_user)

        assert self.model_admin.has_change_permission(
            request, _collection
        ) is False


@pytest.mark.django_db
class TestCollectionAdminIntegration:

    def _payload(self, unit, **overrides):
        payload = {
            "condominium": unit.pk,
            "scope": "05-2026",
            "originalValue": "1.000,00",
            "discountPercent": "10,00",
            "penaltyPercent": "2,00",
            "feesPercent": "1,00",
            "chargesPercent": "0,50",
            "discountDeadline": "2026-05-10",
            "dueDate": "2099-05-10",
            "is_active": "on",
            "credits-TOTAL_FORMS": "0",
            "credits-INITIAL_FORMS": "0",
            "credits-MIN_NUM_FORMS": "0",
            "credits-MAX_NUM_FORMS": "1000",
            "_save": "Salvar",
        }
        payload.update(overrides)
        return payload

    def test_changelist_renders(self, _client, _user, _collection):
        _client.force_login(_user)

        response = _client.get(
            reverse("admin:financial_collection_changelist")
        )

        assert response.status_code == 200
        assert "Cobranças" in response.content.decode()

    def test_add_page_renders(self, _client, _user):
        _client.force_login(_user)

        response = _client.get(reverse("admin:financial_collection_add"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "collection_admin.js" in content
        assert "Composição" in content
        assert "Créditos" in content
        expected_date = date_format(timezone.localdate(), "DATE_FORMAT")
        assert expected_date in content

    def test_add_page_credit_fields_are_optional(self, _client, _user):
        _client.force_login(_user)

        response = _client.get(reverse("admin:financial_collection_add"))

        assert response.status_code == 200
        content = response.content.decode()
        for field in ("financialTransaction", "amountCredit"):
            name = f'name="credits-0-{field}"'
            assert name in content
            start = content.index(name)
            tag_start = content.rindex("<", 0, start)
            tag_end = content.index(">", start)
            assert "required" not in content[tag_start:tag_end]

    def test_tab_order_places_auditoria_last(self, _client, _user):
        _client.force_login(_user)

        response = _client.get(reverse("admin:financial_collection_add"))

        assert response.status_code == 200
        content = response.content.decode()
        nav = content.split('id="jazzy-tabs"', 1)[1].split("</ul>", 1)[0]
        assert nav.index("Principal") < nav.index("Composição")
        assert nav.index("Composição") < nav.index("Créditos")
        assert nav.index("Créditos") < nav.index("Auditoria")

    def test_add_sets_server_fields(self, _client, _user, _unit):
        _client.force_login(_user)

        response = _client.post(
            reverse("admin:financial_collection_add"),
            self._payload(_unit),
        )

        assert response.status_code == 302, response.content
        collection = Collection.objects.get(scope=date(2026, 5, 1))
        assert collection.billingDate is not None
        assert collection.status == Collection.Status.TO_BE_WON
        assert collection.totalAmount == Decimal("935.00")
        assert collection.balance == Decimal("935.00")
        assert collection.created_by == _user

    def test_change_page_renders(self, _client, _user, _collection):
        _client.force_login(_user)

        response = _client.get(
            reverse(
                "admin:financial_collection_change",
                args=[_collection.pk],
            )
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="originalValue"' in content
        assert "composition_table" in content or "Composição" in content

    def test_change_page_has_credit_inline_without_duplicate_table(
        self, _client, _user, _collection
    ):
        _client.force_login(_user)

        response = _client.get(
            reverse(
                "admin:financial_collection_change",
                args=[_collection.pk],
            )
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "credits-TOTAL_FORMS" in content
        assert "Créditos registrados" not in content

    def test_change_page_blocks_expired(
        self, _client, _user, _expired_collection
    ):
        _client.force_login(_user)

        response = _client.post(
            reverse(
                "admin:financial_collection_change",
                args=[_expired_collection.pk],
            ),
            self._payload(
                _expired_collection.condominium,
                scope="02-2026",
                discountDeadline="2026-02-10",
                dueDate="2020-02-10",
            ),
        )

        assert response.status_code == 403
        _expired_collection.refresh_from_db()
        assert _expired_collection.status == Collection.Status.EXPIRED

    def test_change_recalculates_values(self, _client, _user, _collection):
        _client.force_login(_user)

        response = _client.post(
            reverse(
                "admin:financial_collection_change",
                args=[_collection.pk],
            ),
            self._payload(
                _collection.condominium,
                scope="01-2026",
                discountDeadline="2026-01-10",
                dueDate="2099-01-10",
                originalValue="200,00",
                discountPercent="0,00",
                penaltyPercent="",
                feesPercent="",
                chargesPercent="",
            ),
        )

        assert response.status_code == 302, response.content
        _collection.refresh_from_db()
        assert _collection.totalAmount == Decimal("200.00")
        assert _collection.balance == Decimal("200.00")
        assert _collection.updated_by == _user

    def test_delete_to_be_won(self, _client, _user, _collection):
        _client.force_login(_user)
        pk = _collection.pk

        response = _client.post(
            reverse("admin:financial_collection_delete", args=[pk]),
            {"post": "yes"},
        )

        assert response.status_code == 302
        assert not Collection.objects.filter(pk=pk).exists()

    def test_payment_page_renders(self, _client, _user, _collection):
        _client.force_login(_user)

        response = _client.post(
            reverse("admin:financial_collection_changelist"),
            {
                "action": "pagamento",
                "_selected_action": [str(_collection.pk)],
                "select_across": "0",
                "index": "0",
            },
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "Registrar pagamento" in content
        assert f'value="{_collection.pk}"' in content
        assert "js/jquery.mask.min.js" in content
        assert "js/collection_payment_admin.js" in content
        assert 'class="form-control mask-currency"' in content
        assert 'inputmode="decimal"' in content

    def test_payment_action_creates_payment(
        self,
        _client,
        _user,
        _collection,
        _financial_transaction,
    ):
        _client.force_login(_user)
        payload = {
            "action": "pagamento",
            "apply": "1",
            "_selected_action": [str(_collection.pk)],
            "collection": _collection.pk,
            "financialTransaction": _financial_transaction.pk,
            "dateReceived": "2026-01-20",
            "amountReceived": "400,00",
        }

        response = _client.post(
            reverse("admin:financial_collection_changelist"),
            payload,
        )

        assert response.status_code == 302
        payment = Payment.objects.get(collection=_collection)
        assert payment.amountReceived == Decimal("400.00")
        _collection.refresh_from_db()
        assert _collection.status == Collection.Status.PARTIAL
        assert _collection.balance == Decimal("535.00")

    def test_payment_action_rejects_above_balance(
        self,
        _client,
        _user,
        _collection,
        _financial_transaction,
    ):
        _client.force_login(_user)
        payload = {
            "action": "pagamento",
            "apply": "1",
            "_selected_action": [str(_collection.pk)],
            "collection": _collection.pk,
            "financialTransaction": _financial_transaction.pk,
            "dateReceived": "2026-01-20",
            "amountReceived": "1.000,00",
        }

        response = _client.post(
            reverse("admin:financial_collection_changelist"),
            payload,
        )

        assert response.status_code == 200
        assert not Payment.objects.filter(collection=_collection).exists()
        assert "amountReceived" in response.context["form"].errors

    def test_action_update_collections(
        self, _client, _user, _collection
    ):
        _collection.dueDate = date(2020, 1, 10)
        _collection.save(update_fields=["dueDate"])
        _client.force_login(_user)

        response = _client.post(
            reverse("admin:financial_collection_changelist"),
            {
                "action": "atualizar_cobranca",
                "_selected_action": [str(_collection.pk)],
                "select_across": "0",
                "index": "0",
            },
            follow=True,
        )

        assert response.status_code == 200
        _collection.refresh_from_db()
        assert _collection.status == Collection.Status.EXPIRED
        messages = [
            str(message) for message in response.context["messages"]
        ]
        assert any("atualizada" in message for message in messages)

    def test_add_with_credit_updates_balance(
        self,
        _client,
        _user,
        _unit,
        _financial_transaction,
    ):
        _client.force_login(_user)
        payload = self._payload(
            _unit,
            originalValue="100,00",
            discountPercent="",
            penaltyPercent="",
            feesPercent="",
            chargesPercent="",
            **{
                "credits-TOTAL_FORMS": "1",
                "credits-INITIAL_FORMS": "0",
                "credits-0-financialTransaction": _financial_transaction.pk,
                "credits-0-creditDate": "2026-05-10",
                "credits-0-amountCredit": "40,00",
            },
        )

        response = _client.post(
            reverse("admin:financial_collection_add"),
            payload,
        )

        assert response.status_code == 302, response.content
        collection = Collection.objects.get(scope=date(2026, 5, 1))
        assert collection.totalAmount == Decimal("100.00")
        assert collection.balance == Decimal("60.00")
        assert collection.status == Collection.Status.PARTIAL
        assert collection.credits.count() == 1

    def test_add_rejects_credit_above_total(
        self,
        _client,
        _user,
        _unit,
        _financial_transaction,
    ):
        _client.force_login(_user)
        payload = self._payload(
            _unit,
            originalValue="100,00",
            discountPercent="",
            penaltyPercent="",
            feesPercent="",
            chargesPercent="",
            **{
                "credits-TOTAL_FORMS": "1",
                "credits-INITIAL_FORMS": "0",
                "credits-0-financialTransaction": _financial_transaction.pk,
                "credits-0-creditDate": "2026-05-10",
                "credits-0-amountCredit": "150,00",
            },
        )

        response = _client.post(
            reverse("admin:financial_collection_add"),
            payload,
        )

        assert response.status_code == 200
        assert not Collection.objects.filter(
            scope=date(2026, 5, 1)
        ).exists()
        formset = response.context["inline_admin_formsets"][0].formset
        assert any(
            "excede o saldo" in str(error)
            for error in formset.non_form_errors()
        )

    def test_action_delete_collections(
        self, _client, _user, _collection
    ):
        _client.force_login(_user)
        pk = _collection.pk

        response = _client.post(
            reverse("admin:financial_collection_changelist"),
            {
                "action": "excluir_cobrancas",
                "_selected_action": [str(pk)],
                "select_across": "0",
                "index": "0",
            },
            follow=True,
        )

        assert response.status_code == 200
        assert not Collection.objects.filter(pk=pk).exists()
