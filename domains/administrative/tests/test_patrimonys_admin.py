import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.base import BaseStorage
from django.http import HttpRequest
from domains.administrative.admin import PatrimonyAdmin


class _TestMessagesStorage(BaseStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._store = []

    def _get(self, *args, **kwargs):
        return self._store, True

    def _store_messages(self, messages, response, *args, **kwargs):
        self._store = messages
from domains.administrative.models.patrimony import Patrimony
from domains.parameters.models import (
    AssetType, AssetCategory, AssetStatus, AssetStateCondition,
    Addresses, States, TypesCondominium,
)
from domains.condominium.models.condominium import Condominium

@pytest.fixture
def setup_data(db):
    asset_type = AssetType.objects.create(description="Equipamento")
    asset_category = AssetCategory.objects.create(description="Segurança")
    asset_status = AssetStatus.objects.create(description="Ativo")
    state_condition = AssetStateCondition.objects.create(description="Novo")
    state = States.objects.create(name="São Paulo", abbreviation="SP")
    address = Addresses.objects.create(
        zip_code="01001-000", street="Rua Teste", number=100,
        city="São Paulo", state=state,
    )
    type_cond = TypesCondominium.objects.create(name="Residencial")
    condo = Condominium.objects.create(
        code="COND001", name="Condomínio Teste", cnpj="00.000.000/0001-00",
        state_registration="123", municipal_registration="456",
        type_condominium=type_cond, address=address,
    )
    return condo, asset_type, asset_category, asset_status, state_condition

class TestPatrimonyAdmin:
    def test_admin_fieldsets(self, setup_data):
        admin = PatrimonyAdmin(Patrimony, AdminSite())
        assert len(admin.fieldsets) == 5
        fieldset_names = [fs[0] for fs in admin.fieldsets]
        assert "Principal" in fieldset_names
        assert "Aquisições" in fieldset_names
        assert "Manutenções" in fieldset_names
        assert "Documentos" in fieldset_names
        assert "Auditoria" in fieldset_names

    def test_admin_readonly_fields(self, setup_data):
        admin = PatrimonyAdmin(Patrimony, AdminSite())
        assert "asset_code" in admin.readonly_fields
        assert "created_at" in admin.readonly_fields
        assert "updated_at" in admin.readonly_fields

    def test_admin_list_display(self, setup_data):
        admin = PatrimonyAdmin(Patrimony, AdminSite())
        assert "asset_code" in admin.list_display
        assert "name" in admin.list_display
        assert "is_active" in admin.list_display

    def test_admin_list_select_related(self, setup_data):
        admin = PatrimonyAdmin(Patrimony, AdminSite())
        assert "condominium" in admin.list_select_related
        assert "asset_type" in admin.list_select_related
        assert "asset_category" in admin.list_select_related

    def test_generate_asset_code_action(self, setup_data, mocker):
        condo, asset_type, asset_category, asset_status, state_condition = setup_data
        patrimony = Patrimony.objects.create(
            condominium=condo,
            release_date="2026-07-04",
            name="Teste action",
            asset_type=asset_type,
            asset_category=asset_category,
            asset_status=asset_status,
            state_condition=state_condition,
            quantity=1,
            acquisition_date="2026-01-15",
        )
        assert patrimony.asset_code is None

        admin = PatrimonyAdmin(Patrimony, AdminSite())
        request = HttpRequest()
        request._messages = _TestMessagesStorage(request)

        admin.generate_asset_code(request, Patrimony.objects.filter(pk=patrimony.pk))
        patrimony.refresh_from_db()
        assert patrimony.asset_code is not None
        assert patrimony.asset_code.startswith("PAT-")

    def test_generate_asset_code_skips_existing(self, setup_data):
        condo, asset_type, asset_category, asset_status, state_condition = setup_data
        patrimony = Patrimony.objects.create(
            condominium=condo,
            release_date="2026-07-04",
            name="Teste código existente",
            asset_type=asset_type,
            asset_category=asset_category,
            asset_status=asset_status,
            state_condition=state_condition,
            quantity=1,
            acquisition_date="2026-01-15",
            asset_code="PAT-000001",
        )

        admin = PatrimonyAdmin(Patrimony, AdminSite())
        request = HttpRequest()
        request._messages = _TestMessagesStorage(request)

        admin.generate_asset_code(request, Patrimony.objects.filter(pk=patrimony.pk))
        patrimony.refresh_from_db()
        assert patrimony.asset_code == "PAT-000001"
