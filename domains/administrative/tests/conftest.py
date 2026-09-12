import pytest
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import User
from domains.administrative.models import Bank, VirtualMeeting
from domains.condominium.models import Condominium
from domains.email_service.models import (
    ConnectionStatus,
    SMTPConfiguration,
    TypesProvider,
)
from domains.parameters.models import BankAccountType, States, TypesCondominium, Addresses
from domains.parameters.models import VotingType, AssemblyStatus, ResidentType
from domains.residents.models.condominium_unit import CondominiumUnit
from domains.residents.models.resident import Resident


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


@pytest.fixture
def _voting_type():
    return VotingType.objects.create(description='Votação por Aclamação')


@pytest.fixture
def _assembly_status():
    return AssemblyStatus.objects.create(description='Pendente', is_pending=True)


@pytest.fixture
def _resident_type():
    return ResidentType.objects.create(description='Proprietário')


@pytest.fixture
def _condo_unit(_condo):
    return CondominiumUnit.objects.create(
        condominium=_condo,
        tower='A',
        unit_number='101',
        floor='1',
    )


@pytest.fixture
def _resident(_condo_unit, _resident_type):
    return Resident.objects.create(
        unit=_condo_unit,
        type_of_resident=_resident_type,
        name='João da Silva',
        email='joao@example.com',
        phone='(11) 99999-0000',
        cpf='123.456.789-00',
        rg='12.345.678-9',
        sex='M',
        date_of_birth='1990-01-01',
    )


@pytest.fixture
def _user():
    return User.objects.create_user(
        username='admin', password='teste123',
    )


@pytest.fixture
def _provider():
    return TypesProvider.objects.create(provider='SMTP')


@pytest.fixture
def _connection_pendente():
    return ConnectionStatus.objects.create(
        status='Pendente', description='Aguardando envio',
    )


@pytest.fixture
def _connection_enviado():
    return ConnectionStatus.objects.create(
        status='Enviado', description='Enviado com sucesso',
    )


@pytest.fixture
def _smtp_config(_provider):
    return SMTPConfiguration.objects.create(
        description='Test SMTP',
        provider_code='test_smtp',
        provider_type=_provider,
        smtp_host='localhost',
        smtp_port=1025,
        username='test@example.com',
        password='password',
        use_tls=False,
        use_ssl=False,
        api_supported=False,
    )


@pytest.fixture
def _meeting(_condo, _assembly_status):
    now = timezone.now()
    return VirtualMeeting.objects.create(
        condominium=_condo,
        title='Assembleia Geral Ordinária',
        president='João',
        secretary='Maria',
        meeting_status=_assembly_status,
        meeting_date_time_start=now + timezone.timedelta(days=1),
        meeting_date_time_end=now + timezone.timedelta(days=2),
        meeting_date_time_voting_begins=now + timezone.timedelta(days=1, hours=1),
        meeting_date_time_voting_end=now + timezone.timedelta(days=1, hours=2),
        meeting_date_time_send_mail=now + timezone.timedelta(days=1, minutes=30),
        notice_meeting_date_time=now - timezone.timedelta(days=1),
    )
