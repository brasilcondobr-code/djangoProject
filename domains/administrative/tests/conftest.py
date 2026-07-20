import pytest
from decimal import Decimal
from domains.administrative.models import Bank
from domains.condominium.models import Condominium
from domains.parameters.models import BankAccountType, States, TypesCondominium, Addresses


@pytest.fixture
def _state():
    return States.objects.create(name='São Paulo', abbreviation='SP')


@pytest.fixture
def _address(_state):
    return Addresses.objects.create(
        zip_code='01001-000', street='Rua Teste', number=100,
        city='São Paulo', state=_state,
    )


@pytest.fixture
def _type_condo():
    return TypesCondominium.objects.create(name='Prédio')


@pytest.fixture
def _condo(_address, _type_condo):
    return Condominium.objects.create(
        code='COND001', name='Condomínio Teste',
        cnpj='11.222.333/0001-81', state_registration='123456789',
        municipal_registration='987654321',
        type_condominium=_type_condo, address=_address,
    )


@pytest.fixture
def _bank():
    return Bank.objects.create(
        compe=341, bank_name='Itaú', is_active=True,
    )


@pytest.fixture
def _acc_type():
    return BankAccountType.objects.create(description='Conta Corrente')
