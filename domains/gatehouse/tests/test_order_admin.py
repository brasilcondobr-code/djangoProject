from datetime import date
from pathlib import Path

import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.utils import timezone

from domains.gatehouse.admin import OrderAdmin
from domains.gatehouse.forms import OrderForm
from domains.gatehouse.models import Order, OrderPhoto

pytestmark = pytest.mark.django_db

JPEG_BYTES = b"\xFF\xD8\xFF" + b"jpegdata" * 32


def jpg_file(name="encomenda.jpg"):
    return SimpleUploadedFile(name, JPEG_BYTES, content_type="image/jpeg")


class TestOrderAdminConfig:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = OrderAdmin(Order, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert global_admin.site.is_registered(Order)
        assert isinstance(self.admin, OrderAdmin)

    def test_form(self):
        assert self.admin.form == OrderForm

    def test_fieldsets_principal_fields_order(self):
        principal = self.admin.fieldsets[0]
        assert str(principal[0]) == "Principal"
        assert principal[1]["fields"] == (
            "unit",
            "releaseDate",
            "documentNumber",
            "fileImage",
            "observations",
        )

    def test_fieldsets_auditoria_is_last_and_collapsed(self):
        auditoria = self.admin.fieldsets[-1]
        assert str(auditoria[0]) == "Auditoria"
        assert auditoria[1]["fields"] == (
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        )
        assert "collapse" in auditoria[1]["classes"]

    def test_jazzmin_section_order(self):
        assert self.admin.jazzmin_section_order == ["Principal", "Auditoria"]

    def test_readonly_audit_fields(self):
        assert self.admin.readonly_fields == ("created_by", "created_at", "updated_at")

    def test_list_config(self):
        assert self.admin.list_display == (
            "id",
            "unit",
            "releaseDate",
            "documentNumber",
            "is_active",
        )
        assert self.admin.list_filter == ("unit", "is_active")
        assert self.admin.search_fields == (
            "documentNumber",
            "observations",
            "unit__unit_number",
            "unit__condominium__name",
        )
        assert self.admin.ordering == ["-releaseDate", "-id"]
        assert self.admin.list_per_page == 25

    def test_change_permission_not_overridden(self, admin_user):
        request = self.factory.get("/admin/gatehouse/order/")
        request.user = admin_user
        assert "has_change_permission" not in OrderAdmin.__dict__
        assert self.admin.has_change_permission(request) is True

    def test_save_model_sets_created_by_on_create(self, admin_user, unit):
        request = self.factory.post("/admin/gatehouse/order/add/")
        request.user = admin_user
        order = Order(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            fileImage="gatehouse/orders/new.jpg",
        )
        self.admin.save_model(request, order, form=None, change=False)
        assert order.created_by == admin_user

    def test_save_model_preserves_created_by_on_edit(self, admin_user, unit, django_user_model):
        creator = django_user_model.objects.create_superuser(
            username="criador", email="criador@teste.com", password="criador123"
        )
        order = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            fileImage="gatehouse/orders/orig.jpg",
            created_by=creator,
        )
        request = self.factory.post("/admin/gatehouse/order/%s/change/" % order.pk)
        request.user = admin_user
        order.observations = "Editado por outro usuario"
        self.admin.save_model(request, order, form=None, change=True)
        order.refresh_from_db()
        assert order.created_by == creator

    def test_get_queryset_optimized(self, unit):
        request = self.factory.get("/admin/gatehouse/order/")
        request.user = None
        qs = self.admin.get_queryset(request)
        assert "unit" in qs.query.select_related
        assert "condominium" in qs.query.select_related["unit"]
        assert "created_by" in qs.query.select_related

    def test_no_csv_export_action(self):
        actions = getattr(self.admin, "actions", None) or []
        assert "export_as_csv" not in actions

    def test_media_includes_order_admin_js(self):
        assert "js/gatehouse_order_admin.js" in self.admin.Media.js

    def test_order_admin_js_opens_browser_camera(self):
        js_path = (
            Path(__file__).resolve().parents[1]
            / "static"
            / "js"
            / "gatehouse_order_admin.js"
        )
        content = js_path.read_text()
        # botão "Foto" deve abrir a câmera do navegador, não o seletor
        assert "navigator.mediaDevices.getUserMedia" in content
        assert "event.preventDefault()" in content
        assert "Tirar foto" in content
        assert "bc-order-camera" in content
        # fallback para o seletor de arquivos quando a câmera falha
        assert "input.click()" in content


class TestOrderAdminIntegration:

    def _login(self, client, admin_user):
        assert client.login(username="admin", password="admin123")

    def _payload(self, unit, **overrides):
        data = {
            "unit": str(unit.pk),
            "documentNumber": "NF-777",
            "fileImage": jpg_file(),
            "observations": "Caixa média",
            "is_active": "on",
            "_save": "Save",
        }
        data.update(overrides)
        return data

    def test_add_page_renders(self, client, admin_user, unit):
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/order/add/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Principal" in content
        assert "Auditoria" in content
        assert 'id="id_unit"' in content
        assert 'id="id_fileImage"' in content
        assert 'id="id_releaseDate"' in content
        release_line = next(
            line for line in content.splitlines() if 'id="id_releaseDate"' in line
        )
        assert "readonly" in release_line
        # botão Foto na linha de baixo do campo Arquivo
        assert 'for="id_photos"' in content
        assert "Foto" in content
        assert 'name="photos"' in content
        assert 'id="id_photos"' in content
        assert 'accept="image/*"' in content
        assert 'capture="environment"' in content
        assert "multiple" in content
        assert "js/gatehouse_order_admin.js" in content
        # ordem no HTML: input do Arquivo primeiro, botão Foto depois
        assert content.index('id="id_fileImage"') < content.index('id="id_photos"')

    def test_create_via_post_fills_release_date_and_created_by(
        self, client, admin_user, unit
    ):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/order/add/", self._payload(unit), follow=False
        )
        assert response.status_code == 302
        record = Order.objects.get(documentNumber="NF-777")
        assert record.created_by == admin_user
        assert record.unit == unit
        assert record.releaseDate == timezone.localdate()
        assert record.is_active is True
        assert record.fileImage.name.startswith("gatehouse/orders/")
        assert record.observations == "Caixa média"

    def test_create_duplicate_is_rejected(self, client, admin_user, unit):
        self._login(client, admin_user)
        url = "/admin/gatehouse/order/add/"
        client.post(url, self._payload(unit))
        response = client.post(url, self._payload(unit, fileImage=jpg_file("outro.jpg")))
        assert response.status_code == 200
        assert response.context["adminform"].form.errors
        assert Order.objects.filter(documentNumber="NF-777").count() == 1

    def test_create_with_invalid_file_is_rejected(self, client, admin_user, unit):
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/order/add/",
            self._payload(
                unit,
                fileImage=SimpleUploadedFile("encomenda.gif", b"GIF89a" + b"0" * 8),
            ),
        )
        assert response.status_code == 200
        assert response.context["adminform"].form.errors
        assert Order.objects.count() == 0

    def test_edit_updates_record_and_keeps_created_by(
        self, client, admin_user, unit, django_user_model
    ):
        creator = django_user_model.objects.create_superuser(
            username="criador2", email="criador2@teste.com", password="criador123"
        )
        record = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-888",
            fileImage="gatehouse/orders/existente.jpg",
            created_by=creator,
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/order/%s/change/" % record.pk,
            {
                "unit": str(unit.pk),
                "releaseDate": "2026-10-20",
                "documentNumber": "NF-889",
                "observations": "Retirado pelo morador",
                "is_active": "on",
                "_save": "Save",
            },
        )
        assert response.status_code == 302
        record.refresh_from_db()
        assert record.releaseDate == date(2026, 10, 20)
        assert record.documentNumber == "NF-889"
        assert record.observations == "Retirado pelo morador"
        assert record.created_by == creator
        assert record.fileImage.name == "gatehouse/orders/existente.jpg"

    def test_edit_requires_release_date(self, client, admin_user, unit):
        record = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-900",
            fileImage="gatehouse/orders/existente2.jpg",
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/order/%s/change/" % record.pk,
            {
                "unit": str(unit.pk),
                "documentNumber": "NF-900",
                "observations": "",
                "is_active": "on",
                "_save": "Save",
            },
        )
        assert response.status_code == 200
        assert response.context["adminform"].form.errors
        record.refresh_from_db()
        assert record.releaseDate == date(2026, 10, 5)

    def test_delete_via_post(self, client, admin_user, unit):
        record = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-901",
            fileImage="gatehouse/orders/apagar.jpg",
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/order/%s/delete/" % record.pk, {"post": "yes"}
        )
        assert response.status_code == 302
        assert not Order.objects.filter(pk=record.pk).exists()

    def test_change_page_renders(self, client, admin_user, unit):
        record = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-902",
            fileImage="gatehouse/orders/mostrar.jpg",
        )
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/order/%s/change/" % record.pk)
        assert response.status_code == 200
        assert "NF-902" in response.content.decode()

    def test_create_with_multiple_photos(self, client, admin_user, unit):
        self._login(client, admin_user)
        payload = self._payload(unit, documentNumber="NF-FOTOS-ADMIN")
        payload["photos"] = [jpg_file("frente.jpg"), jpg_file("verso.jpg")]
        response = client.post("/admin/gatehouse/order/add/", payload)
        assert response.status_code == 302
        order = Order.objects.get(documentNumber="NF-FOTOS-ADMIN")
        photos = list(order.photos.all())
        assert len(photos) == 2
        assert all(p.file.name.startswith("gatehouse/orders/photos/") for p in photos)
        assert all(p.created_by == admin_user for p in photos)

    def test_create_with_invalid_photo_is_rejected(self, client, admin_user, unit):
        self._login(client, admin_user)
        payload = self._payload(unit, documentNumber="NF-FOTO-RUIM")
        payload["photos"] = [
            SimpleUploadedFile("x.gif", b"GIF89a" + b"0" * 8)
        ]
        response = client.post("/admin/gatehouse/order/add/", payload)
        assert response.status_code == 200
        assert "Formato de arquivo" in response.content.decode()
        assert not Order.objects.filter(documentNumber="NF-FOTO-RUIM").exists()
        assert OrderPhoto.objects.count() == 0

    def test_create_with_photos_only_and_no_file(self, client, admin_user, unit):
        self._login(client, admin_user)
        payload = self._payload(unit, documentNumber="NF-SO-FOTOS")
        payload.pop("fileImage")
        payload["photos"] = [jpg_file("frente.jpg"), jpg_file("verso.jpg")]
        response = client.post("/admin/gatehouse/order/add/", payload)
        assert response.status_code == 302
        order = Order.objects.get(documentNumber="NF-SO-FOTOS")
        assert not order.fileImage.name
        assert order.photos.count() == 2

    def test_create_without_file_and_photos_is_rejected(
        self, client, admin_user, unit
    ):
        self._login(client, admin_user)
        payload = self._payload(unit, documentNumber="NF-SEM-EVIDENCIA")
        payload.pop("fileImage")
        response = client.post("/admin/gatehouse/order/add/", payload)
        assert response.status_code == 200
        assert (
            "Anexe o arquivo ou tire ao menos uma foto."
            in response.content.decode()
        )
        assert not Order.objects.filter(documentNumber="NF-SEM-EVIDENCIA").exists()

    def test_edit_deletes_photo_via_checkbox(self, client, admin_user, unit):
        record = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-FOTO-DEL",
            fileImage="gatehouse/orders/existente.jpg",
        )
        photo = OrderPhoto.objects.create(
            order=record, file="gatehouse/orders/photos/apagar.jpg"
        )
        self._login(client, admin_user)
        response = client.post(
            "/admin/gatehouse/order/%s/change/" % record.pk,
            {
                "unit": str(unit.pk),
                "releaseDate": "2026-10-05",
                "documentNumber": "NF-FOTO-DEL",
                "observations": "",
                "is_active": "on",
                "photo_delete": str(photo.pk),
                "_save": "Save",
            },
        )
        assert response.status_code == 302
        assert not OrderPhoto.objects.filter(pk=photo.pk).exists()
        assert Order.objects.filter(pk=record.pk).exists()

    def test_change_page_lists_attached_photos(self, client, admin_user, unit):
        record = Order.objects.create(
            unit=unit,
            releaseDate=date(2026, 10, 5),
            documentNumber="NF-FOTO-LIST",
            fileImage="gatehouse/orders/existente.jpg",
        )
        photo = OrderPhoto.objects.create(
            order=record, file="gatehouse/orders/photos/listada.jpg"
        )
        self._login(client, admin_user)
        response = client.get("/admin/gatehouse/order/%s/change/" % record.pk)
        content = response.content.decode()
        assert response.status_code == 200
        assert "Fotos anexadas" in content
        assert 'name="photo_delete"' in content
        assert str(photo.pk) in content
