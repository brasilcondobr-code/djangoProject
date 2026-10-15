from datetime import date
from decimal import Decimal

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin import TabularInline
from django.utils import timezone

from domains.gatehouse.admin import BagAdmin, BagItemInline
from domains.gatehouse.forms import BagForm, BagItemForm
from domains.gatehouse.models import Bag, BagItem

pytestmark = pytest.mark.django_db


@pytest.fixture
def sender(collaborator_factory):
    return collaborator_factory("Remetente Bag")


@pytest.fixture
def foreign_sender(inactive_condominium):
    from domains.condominium.models import Collaborator

    return Collaborator.objects.create(
        condominium=inactive_condominium,
        name="Colaborador Externo",
        cpf="CPFBAG021",
        rg="RGBAG21",
        email="bagadminext@teste.com",
        phone_number="11999990031",
    )


@pytest.fixture
def bag(condominium, sender):
    return Bag.objects.create(
        condominium=condominium,
        releaseDate=date(2026, 10, 5),
        title="Malote base",
        sender=sender,
        recipient="Síndico",
        deliveryDate=date(2026, 10, 6),
    )


class TestBagAdminConfig:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = BagAdmin(Bag, self.site)

    def test_admin_registered(self):
        assert global_admin.site.is_registered(Bag)
        assert isinstance(self.admin, BagAdmin)

    def test_form(self):
        assert self.admin.form == BagForm

    def test_fieldsets_principal_fields_order(self):
        principal = self.admin.fieldsets[0]
        assert str(principal[0]) == "Principal"
        assert principal[1]["fields"] == (
            "condominium",
            "releaseDate",
            "title",
            "sender",
            "recipient",
            "deliveryDate",
            "handDelivery",
            "observations",
        )

    def test_fieldsets_auditoria_is_last_and_collapsed(self):
        auditoria = self.admin.fieldsets[-1]
        assert str(auditoria[0]) == "Auditoria"
        assert auditoria[1]["fields"] == (
            "is_active",
            "created_at",
            "updated_at",
        )
        assert "collapse" in auditoria[1]["classes"]

    def test_no_audit_user_readonly(self):
        assert self.admin.readonly_fields == ("created_at", "updated_at")

    def test_jazzmin_section_order(self):
        assert self.admin.jazzmin_section_order == [
            "Principal",
            "Itens",
            "Auditoria",
        ]

    def test_inline_configuration(self):
        assert self.admin.inlines == [BagItemInline]
        inline = self.admin.inlines[0]
        assert issubclass(inline, TabularInline)
        assert inline.model is BagItem
        assert inline.form == BagItemForm
        assert inline.extra == 1
        assert inline.verbose_name_plural == "Itens"
        assert inline.fields == (
            "description",
            "documentNumber",
            "amount",
            "value",
        )

    def test_list_config(self):
        assert self.admin.list_display == (
            "id",
            "condominium",
            "releaseDate",
            "title",
            "sender",
            "recipient",
            "deliveryDate",
            "is_active",
        )
        assert self.admin.list_filter == (
            "condominium",
            "handDelivery",
            "is_active",
        )
        assert self.admin.search_fields == (
            "title",
            "recipient",
            "observations",
            "condominium__name",
            "sender__name",
        )
        assert self.admin.ordering == ["-releaseDate", "-id"]
        assert self.admin.list_per_page == 25

    def test_media(self):
        media = self.admin.Media
        assert "gatehouse/css/bag_admin.css" in media.css["all"]
        assert "js/utils.js" in media.js
        assert "js/gatehouse_bag_admin.js" in media.js

    def test_static_files_exist(self):
        from django.contrib.staticfiles import finders

        assert finders.find("gatehouse/css/bag_admin.css") is not None
        assert finders.find("js/gatehouse_bag_admin.js") is not None

    def test_js_applies_mask_and_delegates(self):
        from django.contrib.staticfiles import finders

        path = finders.find("js/gatehouse_bag_admin.js")
        with open(path, encoding="utf-8") as js_file:
            content = js_file.read()
        assert "BrasilCondoUtils.masks.decimal" in content
        assert "$(document).on" in content

    def test_no_change_permission_override(self):
        assert "has_change_permission" not in BagAdmin.__dict__


class TestBagAdminIntegration:

    def _login(self, client, admin_user):
        assert client.login(username="admin", password="admin123")

    def _payload(self, condominium, sender, **overrides):
        data = {
            "condominium": str(condominium.pk),
            "title": "Malote via admin",
            "sender": str(sender.pk),
            "recipient": "Síndico",
            "deliveryDate": "2026-10-05",
            "handDelivery": "False",
            "is_active": "on",
            "items-TOTAL_FORMS": "0",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "_save": "Salvar",
        }
        data.update(overrides)
        return data

    def _payload_with_items(self, condominium, sender, items, **overrides):
        data = self._payload(condominium, sender, **overrides)
        data["items-TOTAL_FORMS"] = str(len(items))
        for index, item in enumerate(items):
            data["items-%d-id" % index] = item.get("id", "")
            data["items-%d-description" % index] = item.get("description", "")
            data["items-%d-documentNumber" % index] = item.get(
                "documentNumber", ""
            )
            data["items-%d-amount" % index] = str(item.get("amount", 1))
            data["items-%d-value" % index] = item.get("value", "")
            if item.get("delete"):
                data["items-%d-DELETE" % index] = "on"
        return data

    def test_add_page_renders(self, client, admin_user, condominium, sender):
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/bag/add/")
        assert response.status_code == 200
        content = response.content.decode()

        assert 'id="bag_form"' in content
        assert "gatehouse/css/bag_admin.css" in content
        assert "js/gatehouse_bag_admin.js" in content

        for field_id in (
            "id_condominium",
            "id_title",
            "id_sender",
            "id_recipient",
            "id_deliveryDate",
            "id_handDelivery",
        ):
            assert 'id="%s"' % field_id in content
        assert "Sim<" in content
        assert "Não<" in content
        assert 'class="mask-currency"' in content
        assert 'id="id_items-0-description"' in content
        assert 'id="id_items-0-amount"' in content
        assert 'id="id_items-0-value"' in content

        date_line = next(
            line
            for line in content.splitlines()
            if 'id="id_releaseDate"' in line
        )
        assert "readonly" in date_line
        assert 'type="date"' in date_line

        principal_at = content.find("Principal")
        itens_at = content.find("Itens")
        auditoria_at = content.find("Auditoria")
        assert -1 < principal_at < itens_at < auditoria_at

    def test_create_assigns_server_today(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/bag/add/", self._payload(condominium, sender)
        )
        assert response.status_code == 302
        bag = Bag.objects.get()
        assert bag.releaseDate == timezone.localdate()
        assert bag.condominium == condominium
        assert bag.sender == sender
        assert bag.title == "Malote via admin"
        assert bag.recipient == "Síndico"
        assert bag.deliveryDate == date(2026, 10, 5)
        assert bag.handDelivery is False

    def test_create_without_recipient_ok(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        payload = self._payload(condominium, sender)
        payload.pop("recipient")
        response = client.post("/admin/gatehouse/bag/add/", payload)
        assert response.status_code == 302
        bag = Bag.objects.get()
        assert bag.recipient in (None, "")

    def test_create_hand_delivery_defaults_false(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        payload = self._payload(condominium, sender)
        payload.pop("handDelivery")
        response = client.post("/admin/gatehouse/bag/add/", payload)
        assert response.status_code == 302
        assert Bag.objects.get().handDelivery is False

    def test_create_ignores_manipulated_release_date(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/bag/add/",
            self._payload(condominium, sender, releaseDate="2020-01-01"),
        )
        assert response.status_code == 302
        assert Bag.objects.get().releaseDate == timezone.localdate()

    def test_create_with_two_items(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        payload = self._payload_with_items(
            condominium,
            sender,
            [
                {
                    "description": "Contrato de aluguel",
                    "documentNumber": "DOC-1",
                    "amount": 3,
                    "value": "1.234,56",
                },
                {
                    "description": "Recibo de pagamento",
                    "amount": 1,
                    "value": "99,90",
                },
            ],
        )
        response = client.post("/admin/gatehouse/bag/add/", payload)
        assert response.status_code == 302
        bag = Bag.objects.get()
        assert bag.items.count() == 2
        first = bag.items.order_by("id").first()
        assert first.description == "Contrato de aluguel"
        assert first.documentNumber == "DOC-1"
        assert first.amount == 3
        assert first.value == Decimal("1234.56")
        second = bag.items.order_by("id").last()
        assert second.description == "Recibo de pagamento"
        assert second.value == Decimal("99.90")

    def test_create_with_invalid_item_amount_rejected(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        payload = self._payload_with_items(
            condominium,
            sender,
            [{"description": "Item inválido", "amount": 0}],
        )
        response = client.post("/admin/gatehouse/bag/add/", payload)
        assert response.status_code == 200
        body = response.content.decode()
        assert "A quantidade do item deve estar entre 1 e 999." in body
        assert Bag.objects.count() == 0

    def test_create_with_item_missing_description_rejected(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        payload = self._payload_with_items(
            condominium, sender, [{"description": "", "amount": 5}]
        )
        response = client.post("/admin/gatehouse/bag/add/", payload)
        assert response.status_code == 200
        assert Bag.objects.count() == 0

    def test_create_with_malformed_value_rejected(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        payload = self._payload_with_items(
            condominium,
            sender,
            [{"description": "Item", "amount": 1, "value": "abc"}],
        )
        response = client.post("/admin/gatehouse/bag/add/", payload)
        assert response.status_code == 200
        assert "Informe um valor monetário válido." in (
            response.content.decode()
        )
        assert Bag.objects.count() == 0

    def test_create_duplicate_is_rejected(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        Bag.objects.create(
            condominium=condominium,
            releaseDate=timezone.localdate(),
            title="Malote via admin",
            sender=sender,
            recipient="Síndico",
            deliveryDate=date(2026, 10, 5),
        )
        response = client.post(
            "/admin/gatehouse/bag/add/", self._payload(condominium, sender)
        )
        assert response.status_code == 200
        assert "Já existe um malote" in response.content.decode()
        assert Bag.objects.count() == 1

    def test_create_sender_other_condominium_rejected(
        self, client, admin_user, condominium, foreign_sender
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/bag/add/",
            self._payload(condominium, foreign_sender),
        )
        assert response.status_code == 200
        assert "deve pertencer" in response.content.decode()
        assert Bag.objects.count() == 0

    def test_create_without_title_rejected(
        self, client, admin_user, condominium, sender
    ):
        self._login(client, admin_user)
        payload = self._payload(condominium, sender)
        payload.pop("title")
        response = client.post("/admin/gatehouse/bag/add/", payload)
        assert response.status_code == 200
        assert "O título do malote é obrigatório." in (
            response.content.decode()
        )

    def test_change_page_renders_editable_release_date(
        self, client, admin_user, bag
    ):
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/bag/%s/change/" % bag.pk)
        assert response.status_code == 200
        date_line = next(
            line
            for line in response.content.decode().splitlines()
            if 'id="id_releaseDate"' in line
        )
        assert "readonly" not in date_line

    def test_edit_updates_release_date_and_items(
        self, client, admin_user, bag
    ):
        item = BagItem.objects.create(bag=bag, description="Antigo", amount=1)
        self._login(client, admin_user)
        payload = self._payload_with_items(
            bag.condominium,
            bag.sender,
            [
                {
                    "id": str(item.pk),
                    "description": "Corrigido",
                    "amount": 2,
                    "value": "10,00",
                },
                {"description": "Novo item", "amount": 4},
            ],
            title=bag.title,
            recipient=bag.recipient,
            deliveryDate="2026-10-06",
            releaseDate="2026-12-24",
        )
        payload["items-INITIAL_FORMS"] = "1"
        response = client.post(
            "/admin/gatehouse/bag/%s/change/" % bag.pk, payload
        )
        assert response.status_code == 302
        bag.refresh_from_db()
        assert bag.releaseDate == date(2026, 12, 24)
        assert bag.items.count() == 2
        item.refresh_from_db()
        assert item.description == "Corrigido"
        assert item.amount == 2
        assert item.value == Decimal("10.00")

    def test_edit_can_delete_item(self, client, admin_user, bag):
        item = BagItem.objects.create(bag=bag, description="Removível", amount=1)
        self._login(client, admin_user)
        payload = self._payload_with_items(
            bag.condominium,
            bag.sender,
            [{"id": str(item.pk), "description": "Removível", "delete": True}],
            title=bag.title,
            recipient=bag.recipient,
            deliveryDate="2026-10-06",
            releaseDate="2026-10-05",
        )
        payload["items-INITIAL_FORMS"] = "1"
        response = client.post(
            "/admin/gatehouse/bag/%s/change/" % bag.pk, payload
        )
        assert response.status_code == 302
        assert bag.items.count() == 0
        assert not BagItem.objects.filter(pk=item.pk).exists()

    def test_edit_without_release_date_rejected(
        self, client, admin_user, bag
    ):
        self._login(client, admin_user)
        payload = self._payload(
            bag.condominium,
            bag.sender,
            title=bag.title,
            recipient=bag.recipient,
            deliveryDate="2026-10-06",
        )
        payload.pop("releaseDate", None)
        response = client.post(
            "/admin/gatehouse/bag/%s/change/" % bag.pk, payload
        )
        assert response.status_code == 200
        assert response.context["adminform"].form.errors
        bag.refresh_from_db()
        assert bag.releaseDate == date(2026, 10, 5)

    def test_delete_via_post(self, client, admin_user, bag):
        BagItem.objects.create(bag=bag, description="Em cascata", amount=1)
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/bag/%s/delete/" % bag.pk, {"post": "yes"}
        )
        assert response.status_code == 302
        assert not Bag.objects.filter(pk=bag.pk).exists()
        assert BagItem.objects.count() == 0
