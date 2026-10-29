from datetime import date
from decimal import Decimal

import pytest

from domains.condominium.models.condominium import Condominium
from domains.parameters.models import (
    Addresses,
    States,
    TypesCondominium,
    TypesOfMaintenanceReservations,
    TypesOfRental,
)
from domains.reservations.models import Rentals
from domains.residents.models import CondominiumUnit


@pytest.fixture
def state(db):
    return States.objects.create(name="São Paulo", abbreviation="SP")


@pytest.fixture
def address(state):
    return Addresses.objects.create(
        zip_code="01001-000",
        street="Rua Teste",
        number=100,
        city="São Paulo",
        state=state,
    )


@pytest.fixture
def condominium(db, address):
    type_cond = TypesCondominium.objects.create(name="Residencial")
    return Condominium.objects.create(
        code="COND001",
        name="Condomínio Teste",
        cnpj="00.000.000/0001-00",
        state_registration="123",
        municipal_registration="456",
        type_condominium=type_cond,
        address=address,
    )


@pytest.fixture
def unit(condominium):
    return CondominiumUnit.objects.create(
        condominium=condominium,
        tower="A",
        unit_number="101",
        floor="1",
    )


@pytest.fixture
def other_unit(condominium):
    return CondominiumUnit.objects.create(
        condominium=condominium,
        tower="B",
        unit_number="202",
        floor="2",
    )


@pytest.fixture
def rental_type(db):
    return TypesOfRental.objects.create(
        description="Locação de Salão",
        numberOfAppointments=2,
        numberOfReservations=1,
    )


@pytest.fixture
def other_rental_type(db):
    return TypesOfRental.objects.create(
        description="Locação de Churrasqueira",
        numberOfAppointments=2,
        numberOfReservations=1,
    )


@pytest.fixture
def maintenance_type(db):
    return TypesOfMaintenanceReservations.objects.create(
        description="Manutenção Preventiva",
    )


@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_superuser(
        username="admin",
        email="admin@teste.com",
        password="admin123",
    )


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(
        username="outro",
        email="outro@teste.com",
        password="outro123",
    )


@pytest.fixture
def rental_factory(unit, rental_type, admin_user):
    def _create(**kwargs):
        data = {
            "condominium": unit,
            "typesOfRentals": rental_type,
            "startDate": date(2026, 1, 10),
            "endDate": date(2026, 1, 15),
            "applicant": "Solicitante Teste",
            "rentalPrice": Decimal("100.00"),
            "charge_amount": True,
            "observations": "",
            "is_active": True,
            "created_by": admin_user,
            "updated_by": admin_user,
        }
        data.update(kwargs)
        return Rentals.objects.create(**data)

    return _create
