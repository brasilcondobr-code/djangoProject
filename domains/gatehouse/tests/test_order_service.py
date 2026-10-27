from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from domains.gatehouse.exceptions import OrderError
from domains.gatehouse.models import Order, OrderPhoto
from domains.gatehouse.services import OrderService

pytestmark = pytest.mark.django_db

JPEG_BYTES = b"\xFF\xD8\xFF" + b"jpegdata" * 32


def jpg_file(name="encomenda.jpg"):
    return SimpleUploadedFile(name, JPEG_BYTES, content_type="image/jpeg")


class TestOrderServiceCreate:

    def _data(self, unit, **overrides):
        data = {
            "unit": unit,
            "fileImage": jpg_file(),
            "documentNumber": "NF-010",
            "observations": "Caixa frágil",
        }
        data.update(overrides)
        return data

    def test_create_fills_release_date_with_today(self, unit):
        order = OrderService.create_order(self._data(unit))
        assert order.pk is not None
        assert order.releaseDate == timezone.localdate()
        assert order.is_active is True

    def test_create_with_explicit_release_date(self, unit):
        order = OrderService.create_order(
            self._data(unit, releaseDate=date(2026, 10, 5))
        )
        assert order.releaseDate == date(2026, 10, 5)

    def test_create_sets_created_by_for_authenticated_user(self, unit, admin_user):
        order = OrderService.create_order(self._data(unit), user=admin_user)
        assert order.created_by == admin_user

    def test_create_created_by_none_without_user(self, unit):
        order = OrderService.create_order(self._data(unit))
        assert order.created_by is None

    def test_create_receives_unit_as_pk(self, unit):
        data = self._data(unit)
        data["unit"] = unit.pk
        order = OrderService.create_order(data)
        assert order.unit == unit

    def test_create_strips_document_number_to_none(self, unit):
        order = OrderService.create_order(
            self._data(unit, documentNumber="   ")
        )
        assert order.documentNumber is None

    def test_create_missing_unit_raises(self, unit):
        data = self._data(unit)
        del data["unit"]
        with pytest.raises(OrderError) as exc:
            OrderService.create_order(data)
        assert "unit" in str(exc.value)

    def test_create_without_file_or_photos_raises(self, unit):
        data = self._data(unit)
        del data["fileImage"]
        with pytest.raises(OrderError) as exc:
            OrderService.create_order(data)
        assert "Anexe o arquivo ou tire ao menos uma foto." in str(exc.value)

    def test_create_with_photos_only_ok(self, unit, admin_user):
        data = self._data(unit)
        del data["fileImage"]
        photos = [jpg_file("f1.jpg"), jpg_file("f2.jpg")]
        order = OrderService.create_order(data, user=admin_user, photos=photos)
        assert not order.fileImage.name
        assert order.photos.count() == 2

    def test_create_invalid_extension_raises(self, unit):
        data = self._data(
            unit,
            fileImage=SimpleUploadedFile("encomenda.gif", b"GIF89a" + b"0" * 8),
        )
        with pytest.raises(OrderError) as exc:
            OrderService.create_order(data)
        assert "Formato de arquivo" in str(exc.value)

    def test_create_duplicate_raises(self, unit):
        OrderService.create_order(self._data(unit))
        with pytest.raises(OrderError) as exc:
            OrderService.create_order(self._data(unit, fileImage=jpg_file("outro.jpg")))
        assert "Já existe uma encomenda" in str(exc.value)

    def test_create_invalid_release_date_type_raises(self, unit):
        with pytest.raises(OrderError) as exc:
            OrderService.create_order(self._data(unit, releaseDate="não-é-data"))
        assert "Data de lançamento" in str(exc.value)

    def test_create_unknown_unit_pk_raises(self, unit):
        data = self._data(unit)
        data["unit"] = 999999
        with pytest.raises(OrderError) as exc:
            OrderService.create_order(data)
        assert "Unidade não encontrada" in str(exc.value)

    def test_create_invalid_user_keeps_created_by_none(self, unit):
        class NotAuthenticated:
            is_authenticated = False

        order = OrderService.create_order(self._data(unit), user=NotAuthenticated())
        assert order.created_by is None

    def test_create_with_photos(self, unit, admin_user):
        photos = [jpg_file("f1.jpg"), jpg_file("f2.jpg")]
        order = OrderService.create_order(
            self._data(unit), user=admin_user, photos=photos
        )
        rows = list(order.photos.all())
        assert len(rows) == 2
        assert all(p.created_by == admin_user for p in rows)
        assert all(p.file.name.startswith("gatehouse/orders/photos/") for p in rows)

    def test_create_with_invalid_photo_raises(self, unit):
        bad = SimpleUploadedFile("x.gif", b"GIF89a" + b"0" * 8)
        with pytest.raises(OrderError) as exc:
            OrderService.create_order(self._data(unit), photos=[bad])
        assert "Formato de arquivo" in str(exc.value)
        assert Order.objects.count() == 0
        assert OrderPhoto.objects.count() == 0


class TestOrderServiceUpdate:

    @pytest.fixture
    def order(self, unit):
        return Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-020",
            fileImage="gatehouse/orders/orig.jpg",
        )

    def test_update_changes_fields(self, order, other_unit):
        updated = OrderService.update_order(
            order,
            {
                "unit": other_unit,
                "releaseDate": date(2026, 10, 6),
                "documentNumber": "NF-021",
                "observations": "Atualizado",
                "is_active": False,
            },
        )
        updated.refresh_from_db()
        assert updated.unit == other_unit
        assert updated.releaseDate == date(2026, 10, 6)
        assert updated.documentNumber == "NF-021"
        assert updated.observations == "Atualizado"
        assert updated.is_active is False
        assert updated.fileImage.name == "gatehouse/orders/orig.jpg"

    def test_update_partial_keeps_missing_fields(self, order):
        updated = OrderService.update_order(order, {"observations": "Anotação"})
        updated.refresh_from_db()
        assert updated.releaseDate == date(2026, 10, 5)
        assert updated.documentNumber == "NF-020"
        assert updated.observations == "Anotação"

    def test_update_none_instance_raises(self):
        with pytest.raises(OrderError):
            OrderService.update_order(None, {"observations": "x"})

    def test_update_without_release_date_raises(self, order):
        Order.objects.filter(pk=order.pk).update(releaseDate=None)
        order.refresh_from_db()
        with pytest.raises(OrderError) as exc:
            OrderService.update_order(order, {})
        assert "Data de lançamento" in str(exc.value)

    def test_update_duplicate_triple_raises(self, order, unit):
        OrderService.create_order(
            {
                "unit": unit,
                "releaseDate": date(2026, 11, 1),
                "documentNumber": "NF-030",
                "fileImage": jpg_file("outro.jpg"),
            }
        )
        with pytest.raises(OrderError) as exc:
            OrderService.update_order(
                order,
                {"releaseDate": date(2026, 11, 1), "documentNumber": "NF-030"},
            )
        assert "Já existe uma encomenda" in str(exc.value)

    def test_update_same_triple_on_self_not_flagged_as_duplicate(self, order):
        updated = OrderService.update_order(
            order,
            {
                "unit": order.unit,
                "releaseDate": date(2026, 10, 5),
                "documentNumber": "NF-020",
                "observations": "mesma tripla continua valida",
            },
        )
        assert updated.pk == order.pk
        assert updated.observations == "mesma tripla continua valida"

    def test_update_without_file_but_with_photo_ok(self, unit):
        order = Order.objects.create(
            unit=unit, releaseDate=date(2026, 10, 5), documentNumber="NF-040"
        )
        OrderPhoto.objects.create(order=order, file=jpg_file("foto.jpg"))
        updated = OrderService.update_order(order, {"observations": "ok"})
        updated.refresh_from_db()
        assert updated.observations == "ok"

    def test_update_without_file_and_photos_raises(self, unit):
        order = Order.objects.create(
            unit=unit, releaseDate=date(2026, 10, 5), documentNumber="NF-041"
        )
        with pytest.raises(OrderError) as exc:
            OrderService.update_order(order, {"observations": "x"})
        assert "Anexe o arquivo ou tire ao menos uma foto." in str(exc.value)


class TestOrderServiceDelete:

    def test_delete_removes_record(self, unit):
        order = OrderService.create_order(
            {"unit": unit, "fileImage": jpg_file()}
        )
        OrderService.delete_order(order)
        assert not Order.objects.filter(pk=order.pk).exists()

    def test_delete_none_raises(self):
        with pytest.raises(OrderError):
            OrderService.delete_order(None)


class TestOrderServiceQueries:

    def test_get_all_orders_returns_records(self, unit):
        OrderService.create_order(
            {"unit": unit, "fileImage": jpg_file(), "releaseDate": date(2026, 10, 5)}
        )
        OrderService.create_order(
            {"unit": unit, "fileImage": jpg_file("b.jpg"), "releaseDate": date(2026, 10, 6)}
        )
        rows = list(OrderService.get_all_orders())
        assert len(rows) == 2
        assert rows[0].releaseDate >= rows[1].releaseDate

    def test_get_all_orders_empty(self):
        assert list(OrderService.get_all_orders()) == []
