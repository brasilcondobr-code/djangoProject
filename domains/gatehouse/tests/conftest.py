import itertools
from datetime import date

import pytest

from domains.condominium.models.collaborator import Collaborator
from domains.condominium.models.condominium import Condominium
from domains.gatehouse.models import ServiceTransition
from domains.parameters.models import Addresses, ConciergeServiceCategory, States, TypesCondominium


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
def inactive_condominium(db, address, condominium):
    type_cond = TypesCondominium.objects.create(name="Comercial")
    return Condominium.objects.create(
        code="COND002",
        name="Condomínio Inativo",
        cnpj="11.111.111/0001-11",
        state_registration="321",
        municipal_registration="654",
        type_condominium=type_cond,
        address=address,
        is_active=False,
    )


@pytest.fixture
def collaborator_factory(condominium):
    counter = itertools.count(1)

    def _create(name, **kwargs):
        number = next(counter)
        defaults = {
            "condominium": condominium,
            "name": name,
            "cpf": "CPF%09d" % number,
            "rg": "RG%d" % number,
            "email": "colaborador%d@teste.com" % number,
            "phone_number": "1199999%04d" % number,
        }
        defaults.update(kwargs)
        return Collaborator.objects.create(**defaults)

    return _create


@pytest.fixture
def collaborator_out(collaborator_factory):
    return collaborator_factory("Colaborador Saida")


@pytest.fixture
def collaborator_in(collaborator_factory):
    return collaborator_factory("Colaborador Entrada")


@pytest.fixture
def category(db):
    return ConciergeServiceCategory.objects.create(description="Seguranca")


@pytest.fixture
def transition(condominium, collaborator_out, collaborator_in):
    return ServiceTransition.objects.create(
        condominium=condominium,
        collaboratorEnd=collaborator_out,
        collaboratorStart=collaborator_in,
        releaseDate=date(2026, 9, 24),
        observations="Observacao inicial",
    )


@pytest.fixture
def inactive_category(db, category):
    return ConciergeServiceCategory.objects.create(description="Arquivado", is_active=False)


@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_superuser(
        username="admin",
        email="admin@teste.com",
        password="admin123",
    )
