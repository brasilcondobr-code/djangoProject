from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from domains.gatehouse.forms import OrderForm
from domains.gatehouse.models import Order, OrderPhoto

pytestmark = pytest.mark.django_db

JPEG_BYTES = b"\xFF\xD8\xFF" + b"jpegdata" * 32
PDF_BYTES = b"%PDF-1.4\n1 0 obj\n" + b"x" * 64
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"pngdata" * 32


def jpg_file(name="encomenda.jpg"):
    return SimpleUploadedFile(name, JPEG_BYTES, content_type="image/jpeg")


def pdf_file(name="encomenda.pdf"):
    return SimpleUploadedFile(name, PDF_BYTES, content_type="application/pdf")


class TestOrderForm:

    def _data(self, unit, **overrides):
        data = {
            "unit": unit.pk,
            "documentNumber": "NF-001",
            "observations": "",
        }
        data.update(overrides)
        return data

    def _form(self, unit, files=None, photos=None, **overrides):
        if files is None:
            files = {"fileImage": jpg_file()}
        if photos is not None:
            files["photos"] = photos
        return OrderForm(data=self._data(unit, **overrides), files=files)

    def test_form_valid_on_create_fills_release_date(self, unit):
        form = self._form(unit)
        assert form.is_valid(), form.errors
        assert form.cleaned_data["releaseDate"] == timezone.localdate()

    def test_form_valid_with_explicit_release_date(self, unit):
        form = self._form(unit, releaseDate="2026-10-05")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["releaseDate"] == date(2026, 10, 5)

    def test_unit_required(self, unit):
        data = self._data(unit)
        del data["unit"]
        form = OrderForm(data=data)
        assert not form.is_valid()
        assert "unit" in form.errors

    def test_create_without_file_and_photos_rejected(self, unit):
        form = OrderForm(data=self._data(unit), files={})
        assert not form.is_valid()
        assert "fileImage" in form.errors
        assert (
            "Anexe o arquivo ou tire ao menos uma foto."
            in form.errors["fileImage"]
        )

    def test_create_with_photos_only_is_valid(self, unit):
        form = OrderForm(
            data=self._data(unit),
            files={"photos": [jpg_file("foto1.jpg"), jpg_file("foto2.jpg")]},
        )
        assert form.is_valid(), form.errors
        order = form.save()
        assert not order.fileImage.name
        assert order.photos.count() == 2

    def test_invalid_extension_rejected(self, unit):
        form = self._form(
            unit,
            files={
                "fileImage": SimpleUploadedFile(
                    "encomenda.gif", b"GIF89a" + b"0" * 16
                )
            },
        )
        assert not form.is_valid()
        assert "fileImage" in form.errors

    def test_oversize_file_rejected(self, unit):
        big = b"\xFF\xD8\xFF" + b"\0" * (10 * 1024 * 1024)
        form = self._form(
            unit,
            files={
                "fileImage": SimpleUploadedFile(
                    "grande.jpg", big, content_type="image/jpeg"
                )
            },
        )
        assert not form.is_valid()
        assert "fileImage" in form.errors
        assert any("10 MB" in m for m in form.errors["fileImage"])

    def test_pdf_with_wrong_content_rejected(self, unit):
        form = self._form(
            unit,
            files={
                "fileImage": SimpleUploadedFile(
                    "encomenda.pdf", b"nao e um pdf", content_type="application/pdf"
                )
            },
        )
        assert not form.is_valid()
        assert "fileImage" in form.errors
        assert any("conteúdo" in m.lower() for m in form.errors["fileImage"])

    def test_valid_pdf_accepted(self, unit):
        form = self._form(unit, files={"fileImage": pdf_file()})
        assert form.is_valid(), form.errors

    def test_valid_png_accepted(self, unit):
        form = self._form(
            unit,
            files={
                "fileImage": SimpleUploadedFile(
                    "encomenda.png", PNG_BYTES, content_type="image/png"
                )
            },
        )
        assert form.is_valid(), form.errors

    def test_document_number_is_stripped(self, unit):
        form = self._form(unit, documentNumber="  NF-9  ")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["documentNumber"] == "NF-9"

    def test_blank_document_number_becomes_none(self, unit):
        form = self._form(unit, documentNumber="   ")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["documentNumber"] is None

    def test_optional_document_number_and_observations(self, unit):
        form = self._form(unit, documentNumber="", observations="")
        assert form.is_valid(), form.errors

    def test_duplicate_unit_date_document_rejected(self, unit):
        Order.objects.create(
            unit=unit,
            releaseDate=timezone.localdate(),
            documentNumber="NF-001",
            fileImage="gatehouse/orders/exists.jpg",
        )
        form = self._form(unit)
        assert not form.is_valid()
        assert form.non_field_errors()
        assert "fileImage" not in form.errors

    def test_same_date_without_document_is_allowed(self, unit):
        Order.objects.create(
            unit=unit,
            releaseDate=timezone.localdate(),
            fileImage="gatehouse/orders/exists.jpg",
        )
        form = self._form(unit, documentNumber="")
        assert form.is_valid(), form.errors

    def test_create_release_date_readonly_with_initial(self):
        form = OrderForm()
        assert form.fields["releaseDate"].required is False
        assert form.fields["releaseDate"].widget.attrs.get("readonly") == "readonly"
        assert form.fields["releaseDate"].initial == timezone.localdate()

    def test_file_widget_uses_custom_template_without_capture(self):
        form = OrderForm()
        widget = form.fields["fileImage"].widget
        assert widget.template_name == "gatehouse/order_file_input.html"
        assert "capture" not in widget.attrs

    def test_unit_queryset_ordered(self):
        form = OrderForm()
        assert form.fields["unit"].queryset.ordered is True

    def test_edit_requires_release_date(self, unit):
        order = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-001",
            fileImage="gatehouse/orders/exists.jpg",
        )
        form = OrderForm(
            data={
                "unit": unit.pk,
                "documentNumber": "NF-001",
                "observations": "",
            },
            instance=order,
        )
        assert not form.is_valid()
        assert "releaseDate" in form.errors

    def test_edit_keeps_existing_file_when_not_resend(self, unit):
        order = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-001",
            fileImage="gatehouse/orders/exists.jpg",
        )
        form = OrderForm(
            data={
                "unit": unit.pk,
                "releaseDate": "2026-10-06",
                "documentNumber": "NF-001",
                "observations": "Retirado pelo morador",
            },
            instance=order,
        )
        assert form.is_valid(), form.errors
        saved = form.save()
        assert saved.fileImage.name == "gatehouse/orders/exists.jpg"
        assert saved.releaseDate == date(2026, 10, 6)

    def test_edit_allows_same_document_on_other_date(self, unit):
        Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-001",
            fileImage="gatehouse/orders/a.jpg",
        )
        target = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 6),
            documentNumber="NF-002",
            fileImage="gatehouse/orders/b.jpg",
        )
        form = OrderForm(
            data={
                "unit": unit.pk,
                "releaseDate": "2026-10-07",
                "documentNumber": "NF-001",
                "observations": "",
            },
            instance=target,
        )
        assert form.is_valid(), form.errors

    def test_edit_clear_checkbox_without_new_file_keeps_existing(self, unit):
        order = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-001",
            fileImage="gatehouse/orders/exists.jpg",
        )
        form = OrderForm(
            data={
                "unit": unit.pk,
                "releaseDate": "2026-10-05",
                "documentNumber": "NF-001",
                "observations": "",
                "fileImage-clear": "on",
            },
            files={},
            instance=order,
        )
        assert form.is_valid(), form.errors
        saved = form.save()
        assert saved.fileImage.name == "gatehouse/orders/exists.jpg"



def photo_file(name="foto.jpg", content=None):
    if content is None:
        content = b"\xFF\xD8\xFF" + b"foto" * 40
    return SimpleUploadedFile(name, content, content_type="image/jpeg")


class TestOrderFormPhotos:

    def _data(self, unit, **overrides):
        data = {
            "unit": unit.pk,
            "documentNumber": "NF-FOTOS",
            "observations": "",
        }
        data.update(overrides)
        return data

    def _form(self, unit, photos=None, **overrides):
        files = {"fileImage": jpg_file()}
        if photos is not None:
            files["photos"] = photos
        return OrderForm(data=self._data(unit, **overrides), files=files)

    def test_multiple_photos_saved_on_create(self, unit):
        form = self._form(unit, photos=[photo_file("a.jpg"), photo_file("b.jpg")])
        assert form.is_valid(), form.errors
        order = form.save()
        photos = list(order.photos.all())
        assert len(photos) == 2
        assert all(p.file.name.startswith("gatehouse/orders/photos/") for p in photos)
        assert all(p.created_by is None for p in photos)

    def test_no_photos_is_valid(self, unit):
        form = self._form(unit)
        assert form.is_valid(), form.errors
        order = form.save()
        assert order.photos.count() == 0

    def test_photo_with_invalid_extension_rejected(self, unit):
        form = self._form(
            unit,
            photos=[SimpleUploadedFile("x.gif", b"GIF89a" + b"0" * 8)],
        )
        assert not form.is_valid()
        assert "fileImage" in form.errors
        assert any("Formato de arquivo" in m for m in form.errors["fileImage"])

    def test_photo_pdf_rejected(self, unit):
        form = self._form(unit, photos=[pdf_file()])
        assert not form.is_valid()
        assert "fileImage" in form.errors

    def test_photo_oversize_rejected(self, unit):
        big = b"\xFF\xD8\xFF" + b"\0" * (10 * 1024 * 1024)
        form = self._form(
            unit,
            photos=[SimpleUploadedFile("grande.jpg", big, content_type="image/jpeg")],
        )
        assert not form.is_valid()
        assert "fileImage" in form.errors
        assert any("10 MB" in m for m in form.errors["fileImage"])

    def test_photo_wrong_signature_rejected(self, unit):
        form = self._form(unit, photos=[photo_file("falso.jpg", b"nao sou imagem")])
        assert not form.is_valid()
        assert "fileImage" in form.errors
        assert any("conteúdo" in m.lower() for m in form.errors["fileImage"])

    def test_invalid_photo_blocks_save(self, unit):
        form = self._form(unit, photos=[photo_file("ok.jpg"), photo_file("x.gif")])
        assert not form.is_valid()
        assert OrderPhoto.objects.count() == 0

    @pytest.fixture
    def order_with_photo(self, unit):
        order = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-FOTOS",
            fileImage="gatehouse/orders/existente.jpg",
        )
        photo = OrderPhoto.objects.create(
            order=order, file="gatehouse/orders/photos/existente.jpg"
        )
        return order, photo

    def test_edit_delete_photo_via_checkbox(self, order_with_photo):
        order, photo = order_with_photo
        form = OrderForm(
            data={
                "unit": order.unit.pk,
                "releaseDate": "2026-10-05",
                "documentNumber": "NF-FOTOS",
                "observations": "",
                "photo_delete": str(photo.pk),
            },
            instance=order,
        )
        assert form.is_valid(), form.errors
        form.save()
        assert not OrderPhoto.objects.filter(pk=photo.pk).exists()

    def test_edit_keeps_photo_without_checkbox(self, order_with_photo):
        order, photo = order_with_photo
        form = OrderForm(
            data={
                "unit": order.unit.pk,
                "releaseDate": "2026-10-05",
                "documentNumber": "NF-FOTOS",
                "observations": "Mantida",
            },
            instance=order,
        )
        assert form.is_valid(), form.errors
        form.save()
        assert OrderPhoto.objects.filter(pk=photo.pk).exists()

    def test_edit_adds_photo_keeping_existing(self, order_with_photo):
        order, photo = order_with_photo
        form = OrderForm(
            data={
                "unit": order.unit.pk,
                "releaseDate": "2026-10-05",
                "documentNumber": "NF-FOTOS",
                "observations": "",
            },
            files={"photos": [photo_file("nova.jpg")]},
            instance=order,
        )
        assert form.is_valid(), form.errors
        form.save()
        pks = set(order.photos.values_list("pk", flat=True))
        assert photo.pk in pks
        assert len(pks) == 2

    def test_help_text_lists_photos_on_edit(self, order_with_photo):
        order, photo = order_with_photo
        form = OrderForm(instance=order)
        help_text = str(form.fields["fileImage"].help_text)
        assert "Fotos anexadas" in help_text
        assert 'name="photo_delete"' in help_text
        assert str(photo.pk) in help_text

    def test_help_text_on_add_has_no_photo_list(self):
        form = OrderForm()
        help_text = str(form.fields["fileImage"].help_text)
        assert "Fotos anexadas" not in help_text
        assert "photo_delete" not in help_text
