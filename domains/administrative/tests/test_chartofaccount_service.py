import pytest
from domains.administrative.services.chartofaccount_service import ChartOfAccountService
from domains.parameters.models import (
    Chartofaccountstype, Accountingclasstypes,
    ChartofaccountsMaingroup, ChartofaccountsSubgroup,
)


@pytest.mark.django_db
class TestChartOfAccountService:

    def test_get_classes_by_type_returns_active(self):
        acc_type = Chartofaccountstype.objects.create(code='T001', description='Receita', nature='devedora')
        cls1 = Accountingclasstypes.objects.create(
            code='C001', description='Entradas', account_type=acc_type, is_active=True,
        )
        Accountingclasstypes.objects.create(
            code='C002', description='Saídas', account_type=acc_type, is_active=False,
        )
        result = ChartOfAccountService.get_classes_by_type(acc_type.pk)
        assert len(result) == 1
        assert result[0]['id'] == cls1.pk

    def test_get_classes_by_type_empty_id(self):
        assert ChartOfAccountService.get_classes_by_type(None) == []
        assert ChartOfAccountService.get_classes_by_type('') == []

    def test_get_classes_by_type_invalid_id(self):
        assert ChartOfAccountService.get_classes_by_type('abc') == []

    def test_get_classes_by_type_no_results(self):
        acc_type = Chartofaccountstype.objects.create(code='T999', description='Teste', nature='devedora')
        assert ChartOfAccountService.get_classes_by_type(acc_type.pk) == []

    def test_get_groups_by_class_returns_active(self):
        acc_type = Chartofaccountstype.objects.create(code='T001', description='Receita', nature='devedora')
        acc_class = Accountingclasstypes.objects.create(
            code='C001', description='Entradas', account_type=acc_type, is_active=True,
        )
        g1 = ChartofaccountsMaingroup.objects.create(
            code='G001', description='Grupo Teste', account_class=acc_class, is_active=True,
        )
        ChartofaccountsMaingroup.objects.create(
            code='G002', description='Grupo Inativo', account_class=acc_class, is_active=False,
        )
        result = ChartOfAccountService.get_groups_by_class(acc_class.pk)
        assert len(result) == 1
        assert result[0]['id'] == g1.pk

    def test_get_groups_by_class_empty_id(self):
        assert ChartOfAccountService.get_groups_by_class(None) == []
        assert ChartOfAccountService.get_groups_by_class('') == []

    def test_get_groups_by_class_invalid_id(self):
        assert ChartOfAccountService.get_groups_by_class('xyz') == []

    def test_get_subgroups_by_group_returns_active(self):
        acc_type = Chartofaccountstype.objects.create(code='T001', description='Receita', nature='devedora')
        acc_class = Accountingclasstypes.objects.create(
            code='C001', description='Entradas', account_type=acc_type, is_active=True,
        )
        group = ChartofaccountsMaingroup.objects.create(
            code='G001', description='Grupo Teste', account_class=acc_class, is_active=True,
        )
        s1 = ChartofaccountsSubgroup.objects.create(
            code='S001', description='Sub Teste', main_group=group, is_active=True,
        )
        ChartofaccountsSubgroup.objects.create(
            code='S002', description='Sub Inativo', main_group=group, is_active=False,
        )
        result = ChartOfAccountService.get_subgroups_by_group(group.pk)
        assert len(result) == 1
        assert result[0]['id'] == s1.pk

    def test_get_subgroups_by_group_empty_id(self):
        assert ChartOfAccountService.get_subgroups_by_group(None) == []
        assert ChartOfAccountService.get_subgroups_by_group('') == []

    def test_get_subgroups_by_group_invalid_id(self):
        assert ChartOfAccountService.get_subgroups_by_group('abc') == []

    def test_return_values_include_code_and_description(self):
        acc_type = Chartofaccountstype.objects.create(code='T001', description='Receita', nature='devedora')
        acc_class = Accountingclasstypes.objects.create(
            code='C001', description='Entradas', account_type=acc_type, is_active=True,
        )
        result = ChartOfAccountService.get_classes_by_type(acc_type.pk)
        assert len(result) == 1
        assert 'id' in result[0]
        assert 'code' in result[0]
        assert 'description' in result[0]
        assert 'account_type__description' in result[0]
        assert result[0]['code'] == 'C001'
        assert result[0]['description'] == 'Entradas'
        assert result[0]['account_type__description'] == 'Receita'

    def test_return_values_for_groups_include_parent(self):
        acc_type = Chartofaccountstype.objects.create(code='T001', description='Receita', nature='devedora')
        acc_class = Accountingclasstypes.objects.create(
            code='C001', description='Entradas', account_type=acc_type, is_active=True,
        )
        group = ChartofaccountsMaingroup.objects.create(
            code='G001', description='Grupo Teste', account_class=acc_class, is_active=True,
        )
        result = ChartOfAccountService.get_groups_by_class(acc_class.pk)
        assert len(result) == 1
        assert result[0]['account_class__code'] == 'C001'
        assert result[0]['account_class__description'] == 'Entradas'
        assert result[0]['account_class__account_type__description'] == 'Receita'

    def test_return_values_for_subgroups_include_parent(self):
        acc_type = Chartofaccountstype.objects.create(code='T001', description='Receita', nature='devedora')
        acc_class = Accountingclasstypes.objects.create(
            code='C001', description='Entradas', account_type=acc_type, is_active=True,
        )
        group = ChartofaccountsMaingroup.objects.create(
            code='G001', description='Grupo Teste', account_class=acc_class, is_active=True,
        )
        subgroup = ChartofaccountsSubgroup.objects.create(
            code='S001', description='Sub Teste', main_group=group, is_active=True,
        )
        result = ChartOfAccountService.get_subgroups_by_group(group.pk)
        assert len(result) == 1
        assert result[0]['main_group__code'] == 'G001'
        assert result[0]['main_group__description'] == 'Grupo Teste'
        assert result[0]['main_group__account_class__description'] == 'Entradas'
