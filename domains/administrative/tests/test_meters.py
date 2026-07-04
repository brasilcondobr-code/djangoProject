import pytest
from django.core.exceptions import ValidationError
from domains.administrative.models.meters import Meters
from domains.parameters.models.meter_type import MeterType
from domains.residents.models.condominium_unit import CondominiumUnit
from domains.administrative.forms.meter_form import MetersForm

@pytest.fixture
def setup_data(db):
    # Create basic data for testing
    condo_unit = CondominiumUnit.objects.create(
        condominium_id=1, # Assuming a condo exists or using ID
        tower="A",
        unit_number="101",
        floor="1",
    )
    meter_type = MeterType.objects.create(name="Water")
    return condo_unit, meter_type

def test_meters_creation(setup_data):
    condo_unit, meter_type = setup_data
    meter = Meters.objects.create(
        condominium=condo_unit,
        meterType=meter_type,
        unit_identification=condo_unit,
        composition="07/2026",
        Consumption=10.5,
        Value=50.0,
        file="test.jpg",
        is_active=True
    )
    assert meter.pk is not None
    assert str(meter) == f"{condo_unit} - {meter_type} - 07/2026"

def test_meters_uniqueness(setup_data):
    condo_unit, meter_type = setup_data
    Meters.objects.create(
        condominium=condo_unit,
        meterType=meter_type,
        unit_identification=condo_unit,
        composition="07/2026",
        Consumption=10.5,
        Value=50.0,
        file="test1.jpg",
    )
    with pytest.raises(Exception): # UniqueConstraint usually raises IntegrityError
        Meters.objects.create(
            condominium=condo_unit,
            meterType=meter_type,
            unit_identification=condo_unit,
            composition="07/2026",
            Consumption=20.0,
            Value=100.0,
            file="test2.jpg",
        )

def test_meters_form_validation(setup_data):
    condo_unit, meter_type = setup_data
    data = {
        "condominium": condo_unit.pk,
        "releaseDate": "2026-07-04",
        "meterType": meter_type.pk,
        "unit_identification": condo_unit.pk,
        "composition": "13/2026", # Invalid month
        "Consumption": "10.5",
        "Value": "50.0",
        "file": "test.jpg",
    }
    form = MetersForm(data=data)
    assert not form.is_valid()
    assert "composition" in form.errors
