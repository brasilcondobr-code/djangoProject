from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import Client

from domains.administrative.models import ChartOfAccount
from domains.condominium.models import Condominium
from domains.financial.models import NewRelease
from domains.parameters.models import (
    Accountingclasstypes,
    Addresses,
    ChartofaccountsStatus,
    Chartofaccountstype,
    ResidentType,
    States,
    StructionCondominium,
    TypesCondominium,
)
from domains.parameters.models.fund_financial import FundFinancial
from domains.residents.models import CondominiumUnit, Resident


@pytest.fixture
def _state():
    return States.objects.create(name="São Paulo", abbreviation="SP")


@pytest.fixture
def _address(_state):
    return Addresses.objects.create(
        zip_code="01001-000",
        street="Rua Teste",
        number=100,
        city="São Paulo",
        state=_state,
    )


@pytest.fixture
def _type_condo():
    return TypesCondominium.objects.create(name="Prédio")


@pytest.fixture
def _structure_condo():
    return StructionCondominium.objects.create(name="Padrão")


@pytest.fixture
def _condo(_address, _type_condo, _structure_condo):
    return Condominium.objects.create(
        code="COND001",
        name="Condomínio Teste",
        cnpj="11.222.333/0001-81",
        state_registration="123456789",
        municipal_registration="987654321",
        type_condominium=_type_condo,
        struction_condominium=_structure_condo,
        address=_address,
    )


@pytest.fixture
def _condo_two(_state, _type_condo, _structure_condo):
    address = Addresses.objects.create(
        zip_code="02002-000",
        street="Rua Dois",
        number=200,
        city="São Paulo",
        state=_state,
    )
    return Condominium.objects.create(
        code="COND002",
        name="Condomínio Dois",
        cnpj="22.333.444/0001-82",
        state_registration="222222222",
        municipal_registration="333333333",
        type_condominium=_type_condo,
        struction_condominium=_structure_condo,
        address=address,
    )


@pytest.fixture
def _unit(_condo):
    return CondominiumUnit.objects.create(
        condominium=_condo,
        tower="A",
        unit_number="101",
        floor="terreo",
    )


@pytest.fixture
def _unit_two(_condo):
    return CondominiumUnit.objects.create(
        condominium=_condo,
        tower="A",
        unit_number="102",
        floor="1",
    )


@pytest.fixture
def _unit_other_condo(_condo_two):
    return CondominiumUnit.objects.create(
        condominium=_condo_two,
        tower="B",
        unit_number="201",
        floor="2",
    )


def _make_resident(
    unit, name, cpf, email, is_active=True, resident_type=None
):
    return Resident.objects.create(
        unit=unit,
        name=name,
        email=email,
        phone="11999999999",
        cpf=cpf,
        rg=cpf,
        sex="M",
        type_of_resident=resident_type,
        is_active=is_active,
    )


@pytest.fixture
def _resident_type():
    return ResidentType.objects.create(description="Morador(a)")


@pytest.fixture
def _resident(_unit, _resident_type):
    return _make_resident(
        _unit,
        "Morador Um",
        "111.111.111-11",
        "morador1@example.com",
        resident_type=_resident_type,
    )


@pytest.fixture
def _resident_two(_unit_two, _resident_type):
    return _make_resident(
        _unit_two,
        "Morador Dois",
        "222.222.222-22",
        "morador2@example.com",
        resident_type=_resident_type,
    )


@pytest.fixture
def _resident_other_condo(_unit_other_condo, _resident_type):
    return _make_resident(
        _unit_other_condo,
        "Morador Outro",
        "333.333.333-33",
        "morador3@example.com",
        resident_type=_resident_type,
    )


@pytest.fixture
def _resident_inactive(_unit, _resident_type):
    return _make_resident(
        _unit,
        "Morador Inativo",
        "444.444.444-44",
        "morador4@example.com",
        resident_type=_resident_type,
        is_active=False,
    )


@pytest.fixture
def _chart_type():
    return Chartofaccountstype.objects.create(
        code="T001",
        description="Receita",
        nature="credora",
    )


@pytest.fixture
def _account_class(_chart_type):
    return Accountingclasstypes.objects.create(
        code="C001",
        description="Entradas",
        account_type=_chart_type,
    )


@pytest.fixture
def _account_status():
    return ChartofaccountsStatus.objects.create(description="Ativa")


@pytest.fixture
def _chart_account(_condo, _chart_type, _account_class, _account_status):
    return ChartOfAccount.objects.create(
        condominium=_condo,
        account_code="1.1.1",
        account_name="Taxa Condominial",
        account_type=_chart_type,
        account_class=_account_class,
        account_level=1,
        status=_account_status,
        effective_start_date=date(2026, 1, 1),
    )


@pytest.fixture
def _chart_account_other(
    _condo_two, _chart_type, _account_class, _account_status
):
    return ChartOfAccount.objects.create(
        condominium=_condo_two,
        account_code="1.1.1",
        account_name="Taxa Condominial Dois",
        account_type=_chart_type,
        account_class=_account_class,
        account_level=1,
        status=_account_status,
        effective_start_date=date(2026, 1, 1),
    )


@pytest.fixture
def _fund(_condo):
    return FundFinancial.objects.create(
        condominium=_condo,
        description="Fundo de Reserva",
    )


@pytest.fixture
def _fund_other(_condo_two):
    return FundFinancial.objects.create(
        condominium=_condo_two,
        description="Fundo de Reserva Dois",
    )


@pytest.fixture
def _user(db):
    return User.objects.create_superuser(
        username="admin_test",
        email="admin@example.com",
        password="secret123",
    )


@pytest.fixture
def _staff_user(db):
    return User.objects.create_user(
        username="staff_test",
        email="staff@example.com",
        password="secret123",
        is_staff=True,
    )


@pytest.fixture
def _client():
    return Client()


@pytest.fixture
def _new_release(
    _unit, _resident, _chart_account, _fund, _user
):
    return NewRelease.objects.create(
        condominium=_unit,
        paymaster=_resident,
        title="Taxa Condominial",
        scope=date(2026, 1, 1),
        launchDate=date(2026, 1, 10),
        chartOfAccounts=_chart_account,
        fund=_fund,
        launchType=NewRelease.LaunchType.DEBITO,
        value=Decimal("-150.00"),
        created_by=_user,
        updated_by=_user,
    )


@pytest.fixture
def _billing_release(
    _unit, _resident, _chart_account, _fund, _user
):
    return NewRelease.objects.create(
        condominium=_unit,
        paymaster=_resident,
        title="Lançamento Cobrado",
        scope=date(2026, 2, 1),
        launchDate=date(2026, 2, 10),
        chartOfAccounts=_chart_account,
        fund=_fund,
        launchType=NewRelease.LaunchType.DEBITO,
        value=Decimal("-200.00"),
        status=NewRelease.Status.COBRANCA,
        created_by=_user,
        updated_by=_user,
    )


@pytest.fixture
def _valid_form_data(_unit, _resident, _chart_account, _fund):
    return {
        "condominium": _unit.pk,
        "paymaster": _resident.pk,
        "title": "Taxa Condominial",
        "scope": "01-2026",
        "launchDate": "2026-01-10",
        "chartOfAccounts": _chart_account.pk,
        "fund": _fund.pk,
        "launchType": NewRelease.LaunchType.DEBITO,
        "value": "150,00",
        "notes": "",
        "is_active": "on",
    }
