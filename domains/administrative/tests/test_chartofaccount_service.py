import pytest
from domains.administrative.services.chartofaccount_service import ChartOfAccountService
from domains.administrative.models import ChartOfAccount
from domains.condominium.models import Condominium
from domains.parameters.models import (
    Chartofaccountstype, Accountingclasstypes,
    ChartofaccountsStatus, States, Addresses, TypesCondominium,
)


@pytest.fixture
def _state():
    return States.objects.create(name='SP', abbreviation='SP')


@pytest.fixture
def _address(_state):
    return Addresses.objects.create(
        zip_code='01001-000', street='Rua', number=1,
        city='São Paulo', state=_state,
    )


@pytest.fixture
def _type_condo():
    return TypesCondominium.objects.create(name='Casa')


@pytest.fixture
def _condo(_address, _type_condo):
    return Condominium.objects.create(
        code='COND01', name='Condo Teste',
        cnpj='11.222.333/0001-81',
        state_registration='1', municipal_registration='1',
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


@pytest.mark.django_db
class TestChartOfAccountService:

    def test_create_chart_of_account(self, _condo, _acc_type, _acc_class, _status):
        data = {
            'condominium': _condo,
            'account_code': '001.000.000.000',
            'account_name': 'Conta Criada pelo Service',
            'account_type': _acc_type,
            'account_level': 1,
            'account_class': _acc_class,
            'status': _status,
            'effective_start_date': '2024-01-01',
        }
        account = ChartOfAccountService.create_chart_of_account(data)
        assert account.pk is not None
        assert account.account_name == 'Conta Criada pelo Service'

    def test_create_duplicate_code_raises_error(self, _condo, _acc_type, _acc_class, _status):
        data = {
            'condominium': _condo,
            'account_code': '001.000.000.000',
            'account_name': 'Original',
            'account_type': _acc_type,
            'account_level': 1,
            'account_class': _acc_class,
            'status': _status,
            'effective_start_date': '2024-01-01',
        }
        ChartOfAccountService.create_chart_of_account(data)
        with pytest.raises(ValueError, match='Já existe uma conta'):
            ChartOfAccountService.create_chart_of_account(data)

    def test_update_chart_of_account(self, _condo, _acc_type, _acc_class, _status):
        data = {
            'condominium': _condo,
            'account_code': '002.000.000.000',
            'account_name': 'Conta Original',
            'account_type': _acc_type,
            'account_level': 1,
            'account_class': _acc_class,
            'status': _status,
            'effective_start_date': '2024-01-01',
        }
        account = ChartOfAccountService.create_chart_of_account(data)
        updated = ChartOfAccountService.update_chart_of_account(
            account.pk,
            {'account_name': 'Conta Alterada'},
        )
        assert updated is not None
        assert updated.account_name == 'Conta Alterada'

    def test_update_nonexistent_returns_none(self):
        result = ChartOfAccountService.update_chart_of_account(99999, {'account_name': 'Teste'})
        assert result is None

    def test_get_by_id(self, _condo, _acc_type, _acc_class, _status):
        data = {
            'condominium': _condo,
            'account_code': '003.000.000.000',
            'account_name': 'Conta Busca',
            'account_type': _acc_type,
            'account_level': 1,
            'account_class': _acc_class,
            'status': _status,
            'effective_start_date': '2024-01-01',
        }
        account = ChartOfAccountService.create_chart_of_account(data)
        found = ChartOfAccountService.get_chart_of_account_by_id(account.pk)
        assert found is not None
        assert found.account_name == 'Conta Busca'

    def test_get_by_id_not_found(self):
        result = ChartOfAccountService.get_chart_of_account_by_id(99999)
        assert result is None

    def test_get_all(self, _condo, _acc_type, _acc_class, _status):
        for i in range(3):
            ChartOfAccountService.create_chart_of_account({
                'condominium': _condo,
                'account_code': f'00{i}.000.000.000',
                'account_name': f'Conta {i}',
                'account_type': _acc_type,
                'account_level': 1,
                'account_class': _acc_class,
                'status': _status,
                'effective_start_date': '2024-01-01',
            })
        accounts = ChartOfAccountService.get_all_chart_of_accounts()
        assert len(accounts) >= 3
