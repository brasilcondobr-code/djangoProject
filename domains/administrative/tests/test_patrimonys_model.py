import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from domains.administrative.models.patrimony import Patrimony
from domains.parameters.models import (
    AssetType, AssetCategory, AssetStatus, AssetStateCondition,
    AssetBrand, AssetMaintenanceFrequency, Addresses, States, TypesCondominium,
)
from domains.residents.models.condominium_unit import CondominiumUnit
from domains.condominium.models.condominium import Condominium
from domains.personalities.models.entity import Entity
from domains.condominium.models.collaborator import Collaborator

@pytest.fixture
def setup_data(db):
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
    asset_type = AssetType.objects.create(description="Equipamento")
    asset_category = AssetCategory.objects.create(description="Segurança")
    asset_status = AssetStatus.objects.create(description="Ativo")
    state_condition = AssetStateCondition.objects.create(description="Novo")
    asset_brand = AssetBrand.objects.create(description="Intelbras")
    frequency = AssetMaintenanceFrequency.objects.create(description="Mensal")
    return condo, asset_type, asset_category, asset_status, state_condition, asset_brand, frequency

def test_patrimony_creation(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition, asset_brand, frequency = setup_data
    patrimony = Patrimony.objects.create(
        condominium=condo,
        release_date="2026-07-04",
        name="Computador da administração",
        asset_type=asset_type,
        asset_category=asset_category,
        asset_status=asset_status,
        state_condition=state_condition,
        quantity=1,
        acquisition_date="2026-01-15",
    )
    assert patrimony.pk is not None
    assert patrimony.name == "Computador da administração"
    assert str(patrimony) == "SEM CÓDIGO - Computador da administração"

def test_patrimony_str_with_code(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition, asset_brand, frequency = setup_data
    patrimony = Patrimony.objects.create(
        condominium=condo,
        release_date="2026-07-04",
        name="Câmera de segurança",
        asset_type=asset_type,
        asset_category=asset_category,
        asset_status=asset_status,
        state_condition=state_condition,
        quantity=2,
        acquisition_date="2026-01-15",
        asset_code="PAT-000001",
    )
    assert str(patrimony) == "PAT-000001 - Câmera de segurança"

def test_patrimony_asset_code_unique(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition, asset_brand, frequency = setup_data
    Patrimony.objects.create(
        condominium=condo,
        release_date="2026-07-04",
        name="Item 1",
        asset_type=asset_type,
        asset_category=asset_category,
        asset_status=asset_status,
        state_condition=state_condition,
        quantity=1,
        acquisition_date="2026-01-15",
        asset_code="PAT-000001",
    )
    with pytest.raises(IntegrityError):
        Patrimony.objects.create(
            condominium=condo,
            release_date="2026-07-04",
            name="Item 2",
            asset_type=asset_type,
            asset_category=asset_category,
            asset_status=asset_status,
            state_condition=state_condition,
            quantity=1,
            acquisition_date="2026-01-15",
            asset_code="PAT-000001",
        )

def test_patrimony_optional_fields(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition, asset_brand, frequency = setup_data
    patrimony = Patrimony.objects.create(
        condominium=condo,
        release_date="2026-07-04",
        name="Teste campos opcionais",
        asset_type=asset_type,
        asset_category=asset_category,
        asset_status=asset_status,
        state_condition=state_condition,
        quantity=1,
        acquisition_date="2026-01-15",
        serial_number="SN123",
        asset_brand=asset_brand,
        asset_model="Model X",
        description="Descrição teste",
        location="Portaria",
    )
    assert patrimony.serial_number == "SN123"
    assert patrimony.asset_brand.description == "Intelbras"
    assert patrimony.asset_model == "Model X"

def test_patrimony_clean_maintenance_dates(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition, asset_brand, frequency = setup_data
    patrimony = Patrimony(
        condominium=condo,
        release_date="2026-07-04",
        name="Teste manutenção",
        asset_type=asset_type,
        asset_category=asset_category,
        asset_status=asset_status,
        state_condition=state_condition,
        quantity=1,
        acquisition_date="2026-01-15",
        last_maintenance_date="2026-06-01",
        next_maintenance_date="2026-05-01",
    )
    with pytest.raises(ValidationError):
        patrimony.clean()
