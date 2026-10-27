from datetime import date

import pytest
from django import forms
from django.utils import timezone

from domains.condominium.models import Collaborator
from domains.gatehouse.forms import BagForm
from domains.gatehouse.models import Bag

pytestmark = pytest.mark.django_db


@pytest.fixture
def sender(collaborator_factory):
    return collaborator_factory("Remetente Bag")


@pytest.fixture
def foreign_sender(inactive_condominium):
    return Collaborator.objects.create(
        condominium=inactive_condominium,
        name="Colaborador Externo",
        cpf="CPFBAG001",
        rg="RGBAG1",
        email="bagext@teste.com",
        phone_number="11999990011",
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


def _data(**overrides):
    data = {
        "title": "Malote de teste",
        "deliveryDate": "2026-10-05",
        "is_active": "on",
    }
    data.update(overrides)
    return data


def _form(condominium=None, sender=None, **overrides):
    data = _data(**overrides)
    if condominium is not None:
        data["condominium"] = str(condominium.pk)
    if sender is not None:
        data["sender"] = str(sender.pk)
    return BagForm(data=data)


class TestBagForm:

    def test_widgets(self, sender):
        form = BagForm()
        assert (
            form.fields["condominium"].widget.attrs.get("class")
            == "servicetransition-select"
        )
        release = form.fields["releaseDate"]
        assert getattr(release.widget, "input_type", None) == "date"
        assert release.widget.attrs.get("readonly") == "readonly"
        assert release.required is False
        assert release.initial is not None
        assert isinstance(
            form.fields["handDelivery"].widget, forms.RadioSelect
        )
        assert form.fields["recipient"].required is False
        assert form.fields["sender"].queryset.filter(
            is_active=True
        ).exists()

    def test_required_fields(self, condominium, sender):
        form = BagForm(data={})
        assert not form.is_valid()
        for field in ("condominium", "title", "sender", "deliveryDate"):
            assert field in form.errors, field
        assert "recipient" not in form.errors
        assert "O título do malote é obrigatório." in form.errors["title"]
        assert (
            "A data de entrega do malote é obrigatória."
            in form.errors["deliveryDate"]
        )

    def test_create_forces_server_today(self, condominium, sender):
        form = _form(condominium, sender, releaseDate="2020-01-01")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["releaseDate"] == timezone.localdate()

    def test_create_without_release_date_ok(self, condominium, sender):
        form = _form(condominium, sender)
        assert form.is_valid(), form.errors
        assert form.cleaned_data["releaseDate"] == timezone.localdate()

    def test_create_without_recipient_ok(self, condominium, sender):
        form = _form(condominium, sender, recipient="")
        assert form.is_valid(), form.errors
        bag = form.save()
        assert bag.recipient in (None, "")

    def test_edit_release_date_editable_and_required(self, bag):
        form = BagForm(
            data=_data(
                condominium=str(bag.condominium_id),
                title=bag.title,
                sender=str(bag.sender_id),
                recipient=bag.recipient,
                deliveryDate="2026-10-06",
                releaseDate="2026-12-24",
            ),
            instance=bag,
        )
        field = form.fields["releaseDate"]
        assert field.required is True
        assert "readonly" not in field.widget.attrs
        assert form.is_valid(), form.errors
        assert str(form.cleaned_data["releaseDate"]) == "2026-12-24"

    def test_edit_without_release_date_rejected(self, bag):
        form = BagForm(
            data=_data(
                condominium=str(bag.condominium_id),
                title=bag.title,
                sender=str(bag.sender_id),
                deliveryDate="2026-10-06",
            ),
            instance=bag,
        )
        assert not form.is_valid()
        assert "releaseDate" in form.errors

    def test_delivery_date_valid(self, condominium, sender):
        form = _form(condominium, sender, deliveryDate="2026-10-05")
        assert form.is_valid(), form.errors
        assert str(form.cleaned_data["deliveryDate"]) == "2026-10-05"

    def test_delivery_date_invalid_string(self, condominium, sender):
        form = _form(condominium, sender, deliveryDate="nao-é-data")
        assert not form.is_valid()
        assert "deliveryDate" in form.errors

    def test_duplicate_triple_rejected(self, condominium, sender):
        bag = Bag.objects.create(
            condominium=condominium,
            releaseDate=timezone.localdate(),
            title="Malote de teste",
            sender=sender,
            recipient="Síndico",
            deliveryDate=date(2026, 10, 5),
        )
        form = _form(condominium, sender, releaseDate="2099-01-01")
        assert not form.is_valid()
        assert "title" in form.errors
        assert "Já existe um malote" in form.errors["title"][0]
        bag.delete()

    def test_duplicate_different_title_allowed(self, condominium, sender):
        Bag.objects.create(
            condominium=condominium,
            releaseDate=timezone.localdate(),
            title="Outro título",
            sender=sender,
            recipient="Síndico",
            deliveryDate=date(2026, 10, 5),
        )
        form = _form(condominium, sender, title="Malote de teste")
        assert form.is_valid(), form.errors

    def test_edit_same_record_not_flagged_as_duplicate(
        self, condominium, sender
    ):
        bag = Bag.objects.create(
            condominium=condominium,
            releaseDate=timezone.localdate(),
            title="Malote de teste",
            sender=sender,
            recipient="Síndico",
            deliveryDate=date(2026, 10, 5),
        )
        form = BagForm(
            data=_data(
                condominium=str(condominium.pk),
                sender=str(sender.pk),
                releaseDate=timezone.localtime().strftime("%Y-%m-%d"),
                observations="Editado",
            ),
            instance=bag,
        )
        assert form.is_valid(), form.errors

    def test_sender_other_condominium_rejected(
        self, condominium, sender, foreign_sender
    ):
        form = _form(condominium, foreign_sender)
        assert not form.is_valid()
        assert "sender" in form.errors
        assert "deve pertencer ao condomínio" in form.errors["sender"][0]

    def test_sender_queryset_active_preserves_selected(self, bag, sender):
        inactive = Collaborator.objects.create(
            condominium=sender.condominium,
            name="Remetente Inativo",
            cpf="CPFBAG002",
            rg="RGBAG2",
            email="baginativo@teste.com",
            phone_number="11999990012",
            is_active=False,
        )
        bag.sender = inactive
        bag.save()
        form = BagForm(instance=bag)
        names = list(
            form.fields["sender"].queryset.values_list("name", flat=True)
        )
        assert "Remetente Inativo" in names
        assert "Remetente Bag" in names

    def test_title_and_recipient_stripped(self, condominium, sender):
        form = _form(
            condominium,
            sender,
            title="   Título limpo   ",
            recipient="  Síndico  ",
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["title"] == "Título limpo"
        assert form.cleaned_data["recipient"] == "Síndico"

    def test_title_too_long_rejected(self, condominium, sender):
        form = _form(condominium, sender, title="x" * 256)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_observations_optional(self, condominium, sender):
        form = _form(condominium, sender)
        assert form.is_valid(), form.errors
        bag = form.save()
        assert bag.observations in (None, "")
        assert bag.handDelivery is False

    def test_hand_delivery_default_false(self, condominium, sender):
        form = _form(condominium, sender)
        assert form.is_valid(), form.errors
        assert form.cleaned_data["handDelivery"] is False

    def test_hand_delivery_radio_true(self, condominium, sender):
        form = _form(condominium, sender, handDelivery="True")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["handDelivery"] is True

    def test_hand_delivery_radio_false(self, condominium, sender):
        form = _form(condominium, sender, handDelivery="False")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["handDelivery"] is False

    def test_save_sets_server_release_date(self, condominium, sender):
        form = _form(condominium, sender)
        assert form.is_valid(), form.errors
        bag = form.save()
        assert bag.releaseDate == timezone.localdate()
        assert bag.is_active is True
        assert bag.handDelivery is False
