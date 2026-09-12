import pytest
from django.core.exceptions import ValidationError
from domains.administrative.models import ChartOfAccount
from domains.condominium.models import Condominium
from domains.parameters.models import (
    Chartofaccountstype, Accountingclasstypes,
    ChartofaccountsMaingroup, ChartofaccountsSubgroup,
    ChartofaccountsStatus, States, Addresses, TypesCondominium,
)


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
        cnpj='11.222.333/0001-81',
        state_registration='123456789', municipal_registration='987654321',
        type_condominium=_type_condo, address=_address,
        struction_condominium=None,
    )


@pytest.fixture
def _acc_type():
    return Chartofaccountstype.objects.create(code='T001', description='Despesa', nature='devedora')


@pytest.fixture
def _acc_class(_acc_type):
    return Accountingclasstypes.objects.create(code='C001', description='Saídas', account_type=_acc_type)


@pytest.fixture
def _status():
    return ChartofaccountsStatus.objects.create(description='Ativa')


@pytest.fixture
def _account(_condo, _acc_type, _acc_class, _status):
    return ChartOfAccount.objects.create(
        condominium=_condo,
        account_code='001.000.000.000',
        account_name='Conta Teste',
        account_type=_acc_type,
        account_level=1,
        account_class=_acc_class,
        status=_status,
        effective_start_date='2024-01-01',
    )


@pytest.mark.django_db
class TestChartOfAccountModel:

    def test_create_valid(self, _account):
        assert _account.pk is not None
        assert _account.account_code == '001.000.000.000'
        assert _account.account_name == 'Conta Teste'
        assert str(_account) == '001.000.000.000 - Conta Teste'

    def test_required_fields(self):
        with pytest.raises(ValidationError):
            account = ChartOfAccount()
            account.full_clean()

    def test_account_level_validators(self, _condo, _acc_type, _acc_class, _status):
        with pytest.raises(ValidationError):
            account = ChartOfAccount(
                condominium=_condo, account_code='001',
                account_name='Teste', account_type=_acc_type,
                account_level=5, account_class=_acc_class,
                status=_status, effective_start_date='2024-01-01',
            )
            account.full_clean()

        with pytest.raises(ValidationError):
            account = ChartOfAccount(
                condominium=_condo, account_code='001',
                account_name='Teste', account_type=_acc_type,
                account_level=0, account_class=_acc_class,
                status=_status, effective_start_date='2024-01-01',
            )
            account.full_clean()

    def test_unique_code_per_condominium(self, _condo, _acc_type, _acc_class, _status, _account):
        with pytest.raises(Exception):
            ChartOfAccount.objects.create(
                condominium=_condo,
                account_code='001.000.000.000',
                account_name='Outra Conta',
                account_type=_acc_type,
                account_level=1,
                account_class=_acc_class,
                status=_status,
                effective_start_date='2024-01-01',
            )

    def test_same_code_different_condominium(
        self, _address, _type_condo, _acc_type, _acc_class, _status,
    ):
        state = States.objects.create(name='Rio de Janeiro', abbreviation='RJ')
        addr2 = Addresses.objects.create(
            zip_code='20000-000', street='Rua B', number=2,
            city='Rio de Janeiro', state=state,
        )
        condo2 = Condominium.objects.create(
            code='COND002', name='Outro Condomínio',
            cnpj='99.888.777/0001-66',
            state_registration='111', municipal_registration='222',
            type_condominium=_type_condo, address=addr2,
            struction_condominium=None,
        )
        acc1 = ChartOfAccount.objects.create(
            condominium=condo2,
            account_code='001.000.000.000',
            account_name='Conta Réplica',
            account_type=_acc_type,
            account_level=1,
            account_class=_acc_class,
            status=_status,
            effective_start_date='2024-01-01',
        )
        assert acc1.pk is not None

    def test_parent_account_same_condominium(
        self, _condo, _acc_type, _acc_class, _status, _account,
    ):
        child = ChartOfAccount.objects.create(
            condominium=_condo,
            account_code='001.001.000.000',
            account_name='Conta Filha',
            account_type=_acc_type,
            account_level=2,
            account_class=_acc_class,
            status=_status,
            effective_start_date='2024-01-01',
            parent_account=_account,
        )
        assert child.parent_account == _account
        assert child in _account.child_accounts.all()

    def test_default_values(self, _condo, _acc_type, _acc_class, _status):
        account = ChartOfAccount.objects.create(
            condominium=_condo,
            account_code='002.000.000.000',
            account_name='Conta Default',
            account_type=_acc_type,
            account_level=1,
            account_class=_acc_class,
            status=_status,
            effective_start_date='2024-01-01',
        )
        assert account.is_default is False
        assert account.is_system_account is False
        assert account.can_be_archived is True
        assert account.version == '1.0'

    def test_effective_dates(self, _condo, _acc_type, _acc_class, _status):
        account = ChartOfAccount.objects.create(
            condominium=_condo,
            account_code='003.000.000.000',
            account_name='Conta Vigência',
            account_type=_acc_type,
            account_level=1,
            account_class=_acc_class,
            status=_status,
            effective_start_date='2024-01-01',
            effective_end_date='2024-12-31',
        )
        assert account.effective_start_date is not None
        assert account.effective_end_date is not None

    def test_created_at_updated_at(self, _account):
        assert _account.created_at is not None
        assert _account.updated_at is not None
