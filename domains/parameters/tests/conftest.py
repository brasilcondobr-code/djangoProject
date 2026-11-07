import pytest

from domains.condominium.models import Condominium
from domains.parameters.models import Addresses, States, TypesCondominium


def _create_condominium(
    *,
    code,
    cnpj,
    name,
    state_name,
    state_abbreviation,
    street,
    number,
):
    state = States.objects.create(
        name=state_name,
        abbreviation=state_abbreviation,
        capital='Capital',
        region='Região Sudeste',
    )
    address = Addresses.objects.create(
        zip_code='01001-000',
        street=street,
        number=number,
        city='São Paulo',
        state=state,
    )
    type_condominium = TypesCondominium.objects.create(name=f'Tipo {code}')
    return Condominium.objects.create(
        code=code,
        name=name,
        cnpj=cnpj,
        state_registration='123456789',
        municipal_registration='987654321',
        type_condominium=type_condominium,
        address=address,
    )


@pytest.fixture
def fund_condominium(db):
    return _create_condominium(
        code='FUND001',
        cnpj='11.222.333/0001-81',
        name='Condomínio Fundos',
        state_name='São Paulo',
        state_abbreviation='SP',
        street='Rua dos Fundos',
        number=100,
    )


@pytest.fixture
def other_condominium(db):
    """Condomínio diferente, usado nos testes de unicidade."""
    return _create_condominium(
        code='FUND002',
        cnpj='99.888.777/0001-66',
        name='Outro Condomínio Fundos',
        state_name='Rio de Janeiro',
        state_abbreviation='RJ',
        street='Rua de Outro Condomínio',
        number=200,
    )
