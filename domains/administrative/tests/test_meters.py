import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from domains.administrative.models.meters import Meters
from domains.parameters.models.meter_type import MeterType
from domains.residents.models.condominium_unit import CondominiumUnit
from domains.administrative.forms.meter_form import MetersForm


@pytest.fixture
def setup_data(db, _condo):
    condo_unit = CondominiumUnit.objects.create(
        condominium=_condo,
        tower="A",
        unit_number="101",
        floor="1",
    )
    meter_type = MeterType.objects.create(description="Água")
    return condo_unit, meter_type


def test_meters_creation(setup_data):
    condo_unit, meter_type = setup_data
    meter = Meters.objects.create(
        condominium=condo_unit,
        meterType=meter_type,
        composition="07/2026",
        Consumption="10.5",
        Value="50.0",
        is_active=True,
    )
    assert meter.pk is not None
    assert str(meter) == f"{condo_unit} - {meter_type} - 07/2026"


def test_meters_uniqueness(setup_data):
    condo_unit, meter_type = setup_data
    Meters.objects.create(
        condominium=condo_unit,
        meterType=meter_type,
        composition="07/2026",
        Consumption="10.5",
        Value="50.0",
    )
    with pytest.raises(IntegrityError):
        Meters.objects.create(
            condominium=condo_unit,
            meterType=meter_type,
            composition="07/2026",
            Consumption="20.0",
            Value="100.0",
        )


def test_meters_form_validation(setup_data):
    condo_unit, meter_type = setup_data
    data = {
        "condominium": condo_unit.pk,
        "releaseDate": "2026-07-04",
        "meterType": meter_type.pk,
        "composition": "13/2026",
        "Consumption": "10.5",
        "Value": "50.0",
        "file": SimpleUploadedFile("medidor.jpg", b"conteudo", content_type="image/jpeg"),
    }
    form = MetersForm(data=data)
    assert not form.is_valid()
    assert "composition" in form.errors


def test_meters_form_valid(setup_data):
    condo_unit, meter_type = setup_data
    data = {
        "condominium": condo_unit.pk,
        "releaseDate": "2026-07-04",
        "meterType": meter_type.pk,
        "composition": "07/2026",
        "Consumption": "10.5",
        "Value": "50.0",
        "file": SimpleUploadedFile("medidor.jpg", b"conteudo", content_type="image/jpeg"),
    }
    form = MetersForm(data=data)
    assert form.is_valid(), form.errors


def test_meters_invalid_extension(setup_data):
    condo_unit, meter_type = setup_data
    data = {
        "condominium": condo_unit.pk,
        "releaseDate": "2026-07-04",
        "meterType": meter_type.pk,
        "composition": "07/2026",
        "Consumption": "10.5",
        "Value": "50.0",
        "file": SimpleUploadedFile("medidor.exe", b"bad", content_type="application/octet-stream"),
    }
    form = MetersForm(data=data)
    assert not form.is_valid()
    assert "file" in form.errors