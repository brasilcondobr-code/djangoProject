from datetime import date

import pytest
from django.core.exceptions import ValidationError

from domains.gatehouse.models import Order
from domains.residents.models import CondominiumUnit

pytestmark = pytest.mark.django_db


class TestOrderModel:

    @pytest.fixture
    def order(self, unit):
        return Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-2026/001",
            fileImage="gatehouse/orders/encomenda.jpg",
        )

    def test_create_and_str_with_document_number(self, order):
        assert order.pk is not None
        assert str(order) == "Encomenda NF-2026/001"

    def test_str_falls_back_to_release_date(self, unit):
        order = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 6),
            fileImage="gatehouse/orders/b.jpg",
        )
        assert str(order) == "Encomenda 2026-10-06"

    def test_str_empty_instance(self):
        assert str(Order()) == "04. Encomenda"

    def test_meta_verbose(self):
        assert str(Order._meta.verbose_name) == "04. Encomenda"
        assert str(Order._meta.verbose_name_plural) == "04. Encomendas"
        assert Order._meta.app_label == "gatehouse"

    def test_ordering(self):
        assert Order._meta.ordering == ["-releaseDate", "-id"]

    def test_default_is_active(self, unit):
        order = Order.objects.create(
            unit=unit,
            fileImage="gatehouse/orders/c.jpg",
        )
        assert order.is_active is True

    def test_field_null_blank_rules(self):
        get = Order._meta.get_field
        assert get("unit").null is False
        assert get("unit").blank is False
        assert get("releaseDate").null is True
        assert get("releaseDate").blank is True
        assert get("documentNumber").null is True
        assert get("documentNumber").blank is True
        assert get("fileImage").null is False
        assert get("fileImage").blank is True
        assert get("observations").null is True
        assert get("observations").blank is True

    def test_file_field_upload_to(self):
        field = Order._meta.get_field("fileImage")
        assert field.upload_to == "gatehouse/orders/"

    def test_document_number_max_length_255(self):
        field = Order._meta.get_field("documentNumber")
        assert field.max_length == 255

    def test_audit_fields(self):
        assert Order._meta.get_field("created_by").editable is False
        assert Order._meta.get_field("created_at").auto_now_add is True
        assert Order._meta.get_field("updated_at").auto_now is True

    def test_foreign_key_to_condominium_unit(self):
        field = Order._meta.get_field("unit")
        assert field.related_model is CondominiumUnit
        assert field.remote_field.related_name == "orders"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_reverse_relation_orders(self, order, unit):
        assert list(unit.orders.all()) == [order]

    def test_unique_constraint_metadata(self):
        constraint = next(
            c for c in Order._meta.constraints if c.name == "uniq_order_unit_date_doc"
        )
        assert tuple(constraint.fields) == ("unit", "releaseDate", "documentNumber")

    def test_unique_constraint_rejects_duplicate(self, order, unit):
        with pytest.raises(ValidationError):
            duplicate = Order(
                unit=unit,
                releaseDate=date(2026, 10, 5),
                documentNumber="NF-2026/001",
                fileImage="gatehouse/orders/dup.jpg",
            )
            duplicate.full_clean()

    def test_null_document_number_not_treated_as_duplicate(self, unit, other_unit):
        first = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            fileImage="gatehouse/orders/one.jpg",
        )
        second = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            fileImage="gatehouse/orders/two.jpg",
        )
        third = Order.objects.create(
            unit=other_unit,
            releaseDate=date(2026, 10, 5),
            fileImage="gatehouse/orders/three.jpg",
        )
        assert {first.pk, second.pk, third.pk} and second.pk != first.pk
