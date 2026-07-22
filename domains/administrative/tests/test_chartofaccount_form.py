import pytest
from domains.administrative.forms.chartofaccount_form import ChartOfAccountForm
from domains.administrative.models import ChartOfAccount
from domains.condominium.models import Condominium
from domains.parameters.models import (
    Chartofaccountstype, Accountingclasstypes,
    ChartofaccountsMaingroup, ChartofaccountsSubgroup,
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
    return Chartofaccountstype.objects.create(code='T001', description='Receita', nature='devedora')


@pytest.fixture
def _acc_class(_acc_type):
    return Accountingclasstypes.objects.create(code='C001', description='Entradas', account_type=_acc_type)


@pytest.fixture
def _status():
    return ChartofaccountsStatus.objects.create(description='Ativa')


@pytest.mark.django_db
class TestChartOfAccountForm:

    def test_form_widgets_placeholders(self):
        form = ChartOfAccountForm()
        code_widget = form.fields['account_code'].widget
        assert code_widget.attrs.get('placeholder') == 'Ex.: 004.001.002.005'
        name_widget = form.fields['account_name'].widget
        assert name_widget.attrs.get('placeholder') == 'Ex.: Manutenção preventiva de elevadores'

    def test_form_valid(self, _condo, _acc_type, _acc_class, _status):
        data = {
            'condominium': _condo.pk,
            'account_code': '004.001.002.005',
            'account_name': 'Manutenção',
            'account_type': _acc_type.pk,
            'account_level': 1,
            'account_class': _acc_class.pk,
            'status': _status.pk,
            'effective_start_date': '2024-01-01',
        }
        form = ChartOfAccountForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_invalid_without_required(self):
        form = ChartOfAccountForm(data={})
        assert not form.is_valid()
        assert 'condominium' in form.errors
        assert 'account_code' in form.errors
        assert 'account_name' in form.errors
        assert 'account_type' in form.errors
        assert 'account_level' in form.errors
        assert 'account_class' in form.errors
        assert 'status' in form.errors
        assert 'effective_start_date' in form.errors

    def test_form_invalid_code_format(self, _condo, _acc_type, _acc_class, _status):
        data = {
            'condominium': _condo.pk,
            'account_code': 'abc!!!',
            'account_name': 'Conta Inválida',
            'account_type': _acc_type.pk,
            'account_level': 1,
            'account_class': _acc_class.pk,
            'status': _status.pk,
            'effective_start_date': '2024-01-01',
        }
        form = ChartOfAccountForm(data=data)
        assert not form.is_valid()
        assert 'account_code' in form.errors

    def test_form_duplicate_code(self, _condo, _acc_type, _acc_class, _status):
        ChartOfAccount.objects.create(
            condominium=_condo,
            account_code='001.000.000.000',
            account_name='Original',
            account_type=_acc_type,
            account_level=1,
            account_class=_acc_class,
            status=_status,
            effective_start_date='2024-01-01',
        )
        data = {
            'condominium': _condo.pk,
            'account_code': '001.000.000.000',
            'account_name': 'Duplicada',
            'account_type': _acc_type.pk,
            'account_level': 1,
            'account_class': _acc_class.pk,
            'status': _status.pk,
            'effective_start_date': '2024-01-01',
        }
        form = ChartOfAccountForm(data=data)
        assert not form.is_valid()
        assert 'account_code' in form.errors

    def test_form_end_date_before_start(self, _condo, _acc_type, _acc_class, _status):
        data = {
            'condominium': _condo.pk,
            'account_code': '002.000.000.000',
            'account_name': 'Conta Vigência',
            'account_type': _acc_type.pk,
            'account_level': 1,
            'account_class': _acc_class.pk,
            'status': _status.pk,
            'effective_start_date': '2024-12-31',
            'effective_end_date': '2024-01-01',
        }
        form = ChartOfAccountForm(data=data)
        assert not form.is_valid()
        assert 'effective_end_date' in form.errors

    def test_form_parent_account_filter(
        self, _condo, _address, _type_condo, _acc_type, _acc_class, _status,
    ):
        parent = ChartOfAccount.objects.create(
            condominium=_condo,
            account_code='001.000.000.000',
            account_name='Conta Pai',
            account_type=_acc_type,
            account_level=1,
            account_class=_acc_class,
            status=_status,
            effective_start_date='2024-01-01',
        )
        data = {
            'condominium': _condo.pk,
            'account_code': '001.001.000.000',
            'account_name': 'Conta Filha',
            'account_type': _acc_type.pk,
            'account_level': 2,
            'account_class': _acc_class.pk,
            'parent_account': parent.pk,
            'status': _status.pk,
            'effective_start_date': '2024-01-01',
        }
        form = ChartOfAccountForm(data=data)
        assert form.is_valid(), form.errors
