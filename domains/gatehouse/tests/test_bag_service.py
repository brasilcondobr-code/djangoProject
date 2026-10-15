from datetime import date
from decimal import Decimal

import pytest
from django.utils import timezone

from domains.condominium.models import Collaborator
from domains.gatehouse.exceptions import BagError
from domains.gatehouse.models import Bag, BagItem
from domains.gatehouse.services import BagService

pytestmark = pytest.mark.django_db


@pytest.fixture
def sender(collaborator_factory):
    return collaborator_factory("Remetente Bag")


@pytest.fixture
def foreign_sender(inactive_condominium):
    return Collaborator.objects.create(
        condominium=inactive_condominium,
        name="Colaborador Externo",
        cpf="CPFBAG011",
        rg="RGBAG11",
        email="bagsvcext@teste.com",
        phone_number="11999990021",
    )


def _data(condominium=None, sender=None, **overrides):
    data = {
        "title": "Malote de teste",
        "recipient": "Síndico",
        "deliveryDate": date(2026, 10, 5),
    }
    if condominium is not None:
        data["condominium"] = condominium
    if sender is not None:
        data["sender"] = sender
    data.update(overrides)
    return data


class TestBagServiceCreate:

    def test_create_forces_today(self, condominium, sender):
        bag = BagService.create_bag(_data(condominium, sender))
        assert bag.releaseDate == timezone.localdate()
        assert bag.title == "Malote de teste"
        assert bag.recipient == "Síndico"
        assert bag.deliveryDate == date(2026, 10, 5)
        assert bag.is_active is True
        assert bag.handDelivery is False
        assert bag.items.count() == 0

    def test_create_without_recipient_ok(self, condominium, sender):
        bag = BagService.create_bag(_data(condominium, sender, recipient=None))
        assert bag.recipient is None

    def test_create_missing_required_raises(self, condominium, sender):
        with pytest.raises(BagError) as exc:
            BagService.create_bag({"deliveryDate": date(2026, 10, 5)})
        assert "condominium" in str(exc.value)
        assert "title" in str(exc.value)
        assert "sender" in str(exc.value)

    def test_create_accepts_pks(self, condominium, sender):
        bag = BagService.create_bag(
            _data(condominium.pk, sender.pk, title="Por pk")
        )
        assert bag.condominium == condominium
        assert bag.sender == sender

    def test_create_unknown_condominium_raises(self, sender):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(_data(999999, sender))
        assert "Condomínio não encontrado" in str(exc.value)

    def test_create_unknown_sender_raises(self, condominium):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(_data(condominium, 999999))
        assert "Remetente não encontrado" in str(exc.value)

    def test_create_title_stripped(self, condominium, sender):
        bag = BagService.create_bag(
            _data(condominium, sender, title="  Título  ")
        )
        assert bag.title == "Título"

    def test_create_blank_title_raises(self, condominium, sender):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(_data(condominium, sender, title="   "))
        assert "title" in str(exc.value)

    def test_create_title_too_long_raises(self, condominium, sender):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender, title="x" * 256)
            )
        assert "no máximo 255" in str(exc.value)

    def test_create_missing_delivery_date_raises(
        self, condominium, sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender, deliveryDate=None)
            )
        assert "deliveryDate" in str(exc.value)

    def test_create_invalid_delivery_date_value_raises(
        self, condominium, sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender, deliveryDate="xyz")
            )
        assert "entrega" in str(exc.value)

    def test_create_sender_other_condominium_raises(
        self, condominium, foreign_sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(_data(condominium, foreign_sender))
        assert "deve pertencer" in str(exc.value)
        assert Bag.objects.count() == 0

    def test_create_duplicate_raises(self, condominium, sender):
        data = _data(condominium, sender)
        BagService.create_bag(data)
        with pytest.raises(BagError) as exc:
            BagService.create_bag(data)
        assert "Já existe um malote" in str(exc.value)
        assert Bag.objects.count() == 1

    def test_create_with_items(self, condominium, sender):
        bag = BagService.create_bag(
            _data(condominium, sender),
            items=[
                {
                    "description": "Contrato",
                    "documentNumber": "DOC-1",
                    "amount": 2,
                    "value": "1.234,56",
                },
                {
                    "description": "Recibo",
                    "amount": 1,
                    "value": "99,90",
                },
            ],
        )
        assert bag.items.count() == 2
        first = bag.items.first()
        assert first.description == "Contrato"
        assert first.documentNumber == "DOC-1"
        assert first.amount == 2
        assert first.value == Decimal("1234.56")
        second = bag.items.order_by("-id").first()
        assert second.value == Decimal("99.90")

    def test_create_item_missing_description_raises(
        self, condominium, sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender),
                items=[{"description": "", "amount": 1}],
            )
        assert "descrição" in str(exc.value).lower()
        assert Bag.objects.count() == 0

    def test_create_item_amount_zero_raises(self, condominium, sender):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender),
                items=[{"description": "Item", "amount": 0}],
            )
        assert "entre 1 e 999" in str(exc.value)
        assert Bag.objects.count() == 0

    def test_create_item_amount_above_max_raises(
        self, condominium, sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender),
                items=[{"description": "Item", "amount": 1000}],
            )
        assert "entre 1 e 999" in str(exc.value)

    def test_create_item_malformed_value_raises(
        self, condominium, sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender),
                items=[{"description": "Item", "amount": 1, "value": "abc"}],
            )
        assert "monetário" in str(exc.value)
        assert Bag.objects.count() == 0

    def test_create_item_negative_value_raises(self, condominium, sender):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender),
                items=[{"description": "Item", "amount": 1, "value": "-10"}],
            )
        assert "negativo" in str(exc.value)

    def test_create_item_too_many_decimals_raises(
        self, condominium, sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender),
                items=[{"description": "Item", "amount": 1, "value": "1,999"}],
            )
        assert "casas decimais" in str(exc.value)

    def test_create_item_too_many_digits_raises(
        self, condominium, sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(
                _data(condominium, sender),
                items=[
                    {
                        "description": "Item",
                        "amount": 1,
                        "value": "999999999,99",
                    }
                ],
            )
        assert "dígitos" in str(exc.value)

    def test_create_item_without_value_ok(self, condominium, sender):
        bag = BagService.create_bag(
            _data(condominium, sender),
            items=[{"description": "Sem valor", "amount": 1}],
        )
        assert bag.items.first().value is None

    def test_create_item_non_dict_raises(self, condominium, sender):
        with pytest.raises(BagError) as exc:
            BagService.create_bag(_data(condominium, sender), items=["x"])
        assert "Item inválido" in str(exc.value)


class TestBagServiceUpdate:

    @pytest.fixture
    def bag(self, condominium, sender):
        return BagService.create_bag(
            _data(condominium, sender, title="Original"),
            items=[{"description": "Item original", "amount": 1}],
        )

    def test_update_changes_fields(self, bag):
        updated = BagService.update_bag(
            bag,
            {
                "releaseDate": date(2026, 12, 24),
                "title": "Atualizado",
                "recipient": "Diretoria",
                "deliveryDate": date(2026, 12, 25),
                "handDelivery": True,
                "observations": "Nova observação",
                "is_active": False,
            },
        )
        updated.refresh_from_db()
        assert updated.releaseDate == date(2026, 12, 24)
        assert updated.title == "Atualizado"
        assert updated.recipient == "Diretoria"
        assert updated.deliveryDate == date(2026, 12, 25)
        assert updated.handDelivery is True
        assert updated.observations == "Nova observação"
        assert updated.is_active is False

    def test_update_partial_keeps_fields(self, bag):
        updated = BagService.update_bag(bag, {"observations": "Parcial"})
        updated.refresh_from_db()
        assert updated.title == "Original"
        assert updated.condominium == bag.condominium
        assert updated.sender == bag.sender
        assert updated.observations == "Parcial"

    def test_update_none_instance_raises(self):
        with pytest.raises(BagError):
            BagService.update_bag(None, {"title": "x"})

    def test_update_without_release_date_raises(self, bag):
        Bag.objects.filter(pk=bag.pk).update(releaseDate=None)
        bag.refresh_from_db()
        with pytest.raises(BagError):
            BagService.update_bag(bag, {})

    def test_update_duplicate_on_other_raises(
        self, bag, condominium, sender
    ):
        other = BagService.create_bag(
            _data(condominium, sender, title="Outro malote")
        )
        with pytest.raises(BagError) as exc:
            BagService.update_bag(
                other,
                {
                    "releaseDate": bag.releaseDate,
                    "title": bag.title,
                },
            )
        assert "Já existe um malote" in str(exc.value)

    def test_update_same_triple_on_self_ok(self, bag):
        updated = BagService.update_bag(
            bag,
            {
                "releaseDate": bag.releaseDate,
                "title": bag.title,
                "observations": "Mesmo malote",
            },
        )
        assert updated.pk == bag.pk
        assert updated.observations == "Mesmo malote"

    def test_update_sender_other_condominium_raises(
        self, bag, foreign_sender
    ):
        with pytest.raises(BagError) as exc:
            BagService.update_bag(bag, {"sender": foreign_sender})
        assert "deve pertencer" in str(exc.value)
        bag.refresh_from_db()
        assert bag.sender.name == "Remetente Bag"

    def test_update_items_none_keeps(self, bag):
        updated = BagService.update_bag(bag, {"observations": "mantém"})
        assert updated.items.count() == 1

    def test_update_items_empty_clears(self, bag):
        updated = BagService.update_bag(bag, {}, items=[])
        assert updated.items.count() == 0

    def test_update_items_replaces(self, bag):
        updated = BagService.update_bag(
            bag,
            {},
            items=[{"description": "Novo item", "amount": 5, "value": "10,00"}],
        )
        assert updated.items.count() == 1
        item = updated.items.first()
        assert item.description == "Novo item"
        assert item.amount == 5
        assert item.value == Decimal("10.00")

    def test_update_invalid_item_keeps_old(self, bag):
        with pytest.raises(BagError):
            BagService.update_bag(
                bag,
                {},
                items=[{"description": "Novo", "amount": 0}],
            )
        assert bag.items.count() == 1
        assert bag.items.first().description == "Item original"


class TestBagServiceDeleteAndQueries:

    def test_delete_removes_bag_and_items(self, condominium, sender):
        bag = BagService.create_bag(
            _data(condominium, sender),
            items=[{"description": "Apagar", "amount": 1}],
        )
        BagService.delete_bag(bag)
        assert not Bag.objects.filter(pk=bag.pk).exists()
        assert BagItem.objects.count() == 0

    def test_delete_none_raises(self):
        with pytest.raises(BagError):
            BagService.delete_bag(None)

    def test_get_all_returns_bags(self, condominium, sender):
        BagService.create_bag(
            _data(condominium, sender, title="Primeiro"),
            items=[{"description": "A", "amount": 1}],
        )
        BagService.create_bag(
            _data(condominium, sender, title="Segundo"),
        )
        rows = list(BagService.get_all_bags())
        assert len(rows) == 2
        assert rows[0].releaseDate >= rows[1].releaseDate

    def test_get_all_empty(self):
        assert list(BagService.get_all_bags()) == []


class TestBagServiceParseValue:

    def test_parses_br_format(self):
        assert BagService.parse_value("1.234,56") == Decimal("1234.56")

    def test_parses_plain_decimal(self):
        assert BagService.parse_value("0,05") == Decimal("0.05")

    def test_empty_returns_none(self):
        assert BagService.parse_value("") is None
        assert BagService.parse_value(None) is None

    def test_decimal_passthrough_quantized(self):
        assert BagService.parse_value(Decimal("10.5")) == Decimal("10.50")
