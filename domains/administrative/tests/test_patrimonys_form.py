import pytest
from django import forms
from domains.administrative.forms.patrimony_form import PatrimonyForm
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

def test_patrimony_form_valid(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition = setup_data
    form = PatrimonyForm(data={
        "condominium": condo.pk,
        "release_date": "2026-07-04",
        "name": "Computador da administração",
        "asset_type": asset_type.pk,
        "asset_category": asset_category.pk,
        "asset_status": asset_status.pk,
        "state_condition": state_condition.pk,
        "quantity": 1,
        "acquisition_date": "2026-01-15",
    })
    assert form.is_valid(), form.errors

def test_patrimony_form_invalid_without_required(setup_data):
    form = PatrimonyForm(data={})
    assert not form.is_valid()
    assert "release_date" in form.errors
    assert "name" in form.errors
    assert "asset_type" in form.errors
    assert "asset_category" in form.errors
    assert "asset_status" in form.errors
    assert "state_condition" in form.errors
    assert "acquisition_date" in form.errors

def test_patrimony_form_maintenance_dates_validation(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition = setup_data
    form = PatrimonyForm(data={
        "condominium": condo.pk,
        "release_date": "2026-07-04",
        "name": "Teste manutenção",
        "asset_type": asset_type.pk,
        "asset_category": asset_category.pk,
        "asset_status": asset_status.pk,
        "state_condition": state_condition.pk,
        "quantity": 1,
        "acquisition_date": "2026-01-15",
        "last_maintenance_date": "2026-06-01",
        "next_maintenance_date": "2026-05-01",
    })
    assert not form.is_valid()
    assert "next_maintenance_date" in form.errors

def test_patrimony_form_quantity_min_value(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition = setup_data
    form = PatrimonyForm(data={
        "condominium": condo.pk,
        "release_date": "2026-07-04",
        "name": "Teste quantidade",
        "asset_type": asset_type.pk,
        "asset_category": asset_category.pk,
        "asset_status": asset_status.pk,
        "state_condition": state_condition.pk,
        "quantity": 0,
        "acquisition_date": "2026-01-15",
    })
    assert not form.is_valid()

def test_patrimony_form_depreciation_rate_out_of_range(setup_data):
    condo, asset_type, asset_category, asset_status, state_condition = setup_data
    form = PatrimonyForm(data={
        "condominium": condo.pk,
        "release_date": "2026-07-04",
        "name": "Teste depreciação",
        "asset_type": asset_type.pk,
        "asset_category": asset_category.pk,
        "asset_status": asset_status.pk,
        "state_condition": state_condition.pk,
        "quantity": 1,
        "acquisition_date": "2026-01-15",
        "depreciation_rate": "150",
    })
    assert not form.is_valid()
