from datetime import date
from decimal import Decimal

import pytest
from django.core.validators import MaxValueValidator, MinValueValidator

from domains.condominium.models import Collaborator
from domains.gatehouse.models import Bag, BagItem

pytestmark = pytest.mark.django_db


@pytest.fixture
def sender(collaborator_factory):
    return collaborator_factory("Remetente Bag")


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


class TestBagModel:

    def test_create_and_str(self, condominium, sender):
        bag = Bag.objects.create(
            condominium=condominium,
            releaseDate=date(2026, 10, 5),
            title="Documentação",
            sender=sender,
            recipient="Síndico",
            deliveryDate=date(2026, 10, 6),
        )
        assert "Documentação" in str(bag)
        assert str(condominium) in str(bag)

    def test_str_without_condominium(self, sender):
        bag = Bag.objects.create(
            condominium=None,
            title="Sem condomínio",
            sender=sender,
            recipient="Diretoria",
            deliveryDate=date(2026, 10, 6),
        )
        assert str(bag) == "Malote Sem condomínio"

    def test_str_without_title(self, condominium, sender):
        bag = Bag.objects.create(
            condominium=condominium,
            title="",
            sender=sender,
            recipient="Diretoria",
            deliveryDate=date(2026, 10, 6),
        )
        assert str(bag).startswith("Malote sem título")

    def test_meta(self):
        assert Bag._meta.app_label == "gatehouse"
        assert Bag._meta.verbose_name == "08. Malote"
        assert Bag._meta.verbose_name_plural == "08. Malotes"
        assert Bag._meta.ordering == ["-releaseDate", "-id"]

    def test_field_rules(self):
        get = Bag._meta.get_field
        assert get("condominium").null is True
        assert get("condominium").blank is False
        assert get("condominium").remote_field.related_name == "condominium"
        assert get("condominium").remote_field.on_delete.__name__ == "CASCADE"
        assert get("condominium").verbose_name == "Condomínio"
        assert get("releaseDate").null is True
        assert get("releaseDate").blank is True
        assert get("title").null is False
        assert get("title").max_length == 255
        assert get("sender").null is True
        assert get("sender").blank is False
        assert get("sender").remote_field.related_name == "sent_bags"
        assert get("recipient").null is True
        assert get("recipient").blank is True
        assert get("recipient").max_length == 255
        assert get("deliveryDate").null is True
        assert get("deliveryDate").blank is False
        assert get("handDelivery").null is True
        assert get("handDelivery").default is False
        assert get("observations").null is True
        assert get("observations").blank is True
        assert get("is_active").default is True
        assert get("created_at").auto_now_add is True
        assert get("updated_at").auto_now is True

    def test_no_audit_user_fields(self):
        names = {f.name for f in Bag._meta.get_fields()}
        assert "created_by" not in names
        assert "created_user" not in names

    def test_unique_constraint(self):
        constraint = next(
            c
            for c in Bag._meta.constraints
            if c.name == "uniq_bag_condominium_date_title_sender"
        )
        assert set(constraint.fields) == {
            "condominium",
            "releaseDate",
            "title",
            "sender",
        }

    def test_reverse_accessors(self, bag, condominium, sender):
        assert list(condominium.condominium.all()) == [bag]
        assert list(sender.sent_bags.all()) == [bag]

    def test_default_is_active_and_optional_fields(
        self, condominium, sender
    ):
        bag = Bag.objects.create(
            condominium=condominium,
            title="Padrões",
            sender=sender,
            deliveryDate=date(2026, 10, 6),
        )
        assert bag.is_active is True
        assert bag.releaseDate is None
        assert bag.handDelivery is False
        assert bag.recipient is None
        assert bag.observations is None
        assert bag.items.count() == 0


class TestBagItemModel:

    def test_create_and_str(self, bag):
        item = BagItem.objects.create(
            bag=bag,
            description="Contrato de aluguel",
            documentNumber="DOC-01",
            amount=3,
            value=Decimal("1234.56"),
        )
        assert "Contrato de aluguel" in str(item)
        assert "x3" in str(item)
        assert item.value == Decimal("1234.56")

    def test_field_rules(self):
        get = BagItem._meta.get_field
        assert get("bag").remote_field.related_name == "items"
        assert get("bag").remote_field.on_delete.__name__ == "CASCADE"
        assert get("description").null is False
        assert get("description").max_length == 255
        assert get("documentNumber").null is True
        assert get("documentNumber").blank is True
        assert get("documentNumber").max_length == 30
        assert get("amount").default == 1
        assert get("amount").null is False
        limit_values = [v.limit_value for v in get("amount").validators]
        assert 1 in limit_values
        assert 999 in limit_values
        assert any(isinstance(v, MinValueValidator) for v in get("amount").validators)
        assert any(isinstance(v, MaxValueValidator) for v in get("amount").validators)
        assert get("value").null is True
        assert get("value").blank is True
        assert get("value").max_digits == 10
        assert get("value").decimal_places == 2

    def test_meta(self):
        assert BagItem._meta.verbose_name == "08. Item de Malote"
        assert BagItem._meta.verbose_name_plural == "08. Itens de Malote"
        assert BagItem._meta.ordering == ["id"]

    def test_reverse_accessor_and_cascade(self, bag):
        BagItem.objects.create(bag=bag, description="Item único", amount=1)
        assert bag.items.count() == 1
        bag.delete()
        assert BagItem.objects.count() == 0

    def test_optional_item_fields(self, bag):
        item = BagItem.objects.create(bag=bag, description="Sem extras")
        assert item.documentNumber is None
        assert item.amount == 1
        assert item.value is None
