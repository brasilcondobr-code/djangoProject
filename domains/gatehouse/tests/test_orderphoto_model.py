from datetime import date

import pytest

from domains.gatehouse.models import Order, OrderPhoto

pytestmark = pytest.mark.django_db


class TestOrderPhotoModel:

    @pytest.fixture
    def order(self, unit):
        return Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-FOTO",
            fileImage="gatehouse/orders/note.pdf",
        )

    @pytest.fixture
    def photo(self, order):
        return OrderPhoto.objects.create(
            order=order,
            file="gatehouse/orders/photos/frente.jpg",
        )

    def test_create_and_str(self, photo, order):
        assert photo.pk is not None
        assert str(photo) == "Foto %s — %s" % (photo.pk, order)

    def test_str_without_order(self):
        assert str(OrderPhoto()) == "Foto de Encomenda"

    def test_meta_verbose(self):
        assert str(OrderPhoto._meta.verbose_name) == "Foto de Encomenda"
        assert str(OrderPhoto._meta.verbose_name_plural) == "Fotos de Encomenda"
        assert OrderPhoto._meta.app_label == "gatehouse"
        assert OrderPhoto._meta.ordering == ["id"]

    def test_field_rules(self):
        get = OrderPhoto._meta.get_field
        assert get("order").null is False
        assert get("order").blank is False
        assert get("file").null is False
        assert get("file").blank is False
        assert get("file").upload_to == "gatehouse/orders/photos/"

    def test_foreign_key_related_name_photos(self, photo, order):
        field = OrderPhoto._meta.get_field("order")
        assert field.related_model is Order
        assert field.remote_field.related_name == "photos"
        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert list(order.photos.all()) == [photo]

    def test_audit_fields(self):
        assert OrderPhoto._meta.get_field("created_by").editable is False
        assert OrderPhoto._meta.get_field("created_at").auto_now_add is True
        assert OrderPhoto._meta.get_field("updated_at").auto_now is True

    def test_order_delete_cascades_photos(self, photo, order):
        order_pk, photo_pk = order.pk, photo.pk
        order.delete()
        assert not OrderPhoto.objects.filter(pk=photo_pk).exists()
        assert not Order.objects.filter(pk=order_pk).exists()
