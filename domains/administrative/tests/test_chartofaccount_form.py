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

    def test_dependent_fields_show_all_active_on_add(self, _acc_type, _acc_class):
        form = ChartOfAccountForm()
        assert form.fields['account_class'].queryset.count() == 1
        assert _acc_class in form.fields['account_class'].queryset
        assert form.fields['account_group'].queryset.count() == 0
        assert form.fields['account_subgroup'].queryset.count() == 0

    def test_form_rejects_class_not_belonging_to_type(self, _condo, _acc_type, _acc_class, _status):
        other_type = Chartofaccountstype.objects.create(code='T002', description='Passivo', nature='credora')
        data = {
            'condominium': _condo.pk,
            'account_code': '005.000.000.000',
            'account_name': 'Hierarquia Inválida',
            'account_type': other_type.pk,
            'account_level': 1,
            'account_class': _acc_class.pk,
            'status': _status.pk,
            'effective_start_date': '2024-01-01',
        }
        form = ChartOfAccountForm(data=data)
        assert not form.is_valid()
        assert 'account_class' in form.errors

    def test_form_rejects_group_not_belonging_to_class(
        self, _condo, _acc_type, _acc_class, _status,
    ):
        other_class = Accountingclasstypes.objects.create(
            code='C002', description='Saídas', account_type=_acc_type,
        )
        group = ChartofaccountsMaingroup.objects.create(
            code='G001', description='Grupo Teste', account_class=other_class,
        )
        data = {
            'condominium': _condo.pk,
            'account_code': '006.000.000.000',
            'account_name': 'Grupo Inválido',
            'account_type': _acc_type.pk,
            'account_level': 1,
            'account_class': _acc_class.pk,
            'account_group': group.pk,
            'status': _status.pk,
            'effective_start_date': '2024-01-01',
        }
        form = ChartOfAccountForm(data=data)
        assert not form.is_valid()
        assert 'account_group' in form.errors

    def test_form_data_ajax_attributes(self):
        form = ChartOfAccountForm()
        assert form.fields['account_type'].widget.attrs.get('data-classes-url') is not None
        assert form.fields['account_class'].widget.attrs.get('data-groups-url') is not None
        assert form.fields['account_group'].widget.attrs.get('data-subgroups-url') is not None

    def test_edit_mode_queryset_restricted_to_related(
        self, _condo, _acc_type, _acc_class, _status,
    ):
        Chartofaccountstype.objects.create(code='T002', description='Passivo', nature='credora')
        account = ChartOfAccount.objects.create(
            condominium=_condo,
            account_code='001.000.000.000',
            account_name='Conta Edit',
            account_type=_acc_type,
            account_level=1,
            account_class=_acc_class,
            status=_status,
            effective_start_date='2024-01-01',
        )
        form = ChartOfAccountForm(instance=account)
        qs = form.fields['account_class'].queryset
        assert _acc_class in qs
        assert qs.count() == 1

    def test_form_rejects_subgroup_not_belonging_to_group(
        self, _condo, _acc_type, _acc_class, _status,
    ):
        group = ChartofaccountsMaingroup.objects.create(
            code='G001', description='Grupo Teste', account_class=_acc_class,
        )
        other_group = ChartofaccountsMaingroup.objects.create(
            code='G002', description='Outro Grupo', account_class=_acc_class,
        )
        subgroup = ChartofaccountsSubgroup.objects.create(
            code='S001', description='Sub Teste', main_group=other_group,
        )
        data = {
            'condominium': _condo.pk,
            'account_code': '007.000.000.000',
            'account_name': 'Subgrupo Inválido',
            'account_type': _acc_type.pk,
            'account_level': 1,
            'account_class': _acc_class.pk,
            'account_group': group.pk,
            'account_subgroup': subgroup.pk,
            'status': _status.pk,
            'effective_start_date': '2024-01-01',
        }
        form = ChartOfAccountForm(data=data)
        assert not form.is_valid()
        assert 'account_subgroup' in form.errors
