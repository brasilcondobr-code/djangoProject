import pytest
from decimal import Decimal
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from domains.administrative.models import Bank, BankAccount
from domains.administrative.admin import BankAccountAdmin
from domains.administrative.forms import BankAccountForm
from domains.parameters.models import BankAccountType


@pytest.mark.django_db
class TestBankAccountAdmin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = BankAccountAdmin(BankAccount, self.site)

    def test_admin_registered(self):
        assert self.admin is not None

    def test_admin_form(self):
        assert self.admin.form == BankAccountForm

    def test_admin_list_display(self):
        expected = (
            'bank', 'condominium', 'account_type', 'account_name',
            'agency', 'account_number', 'account_digit', 'initial_balance',
            'is_active', 'created_at',
        )
        assert self.admin.list_display == expected

    def test_admin_list_filter(self):
        expected = ('bank', 'condominium', 'account_type', 'is_active')
        assert self.admin.list_filter == expected

    def test_admin_search_fields(self):
        expected = (
            'account_name', 'agency', 'account_number', 'account_digit',
            'bank__bank_name', 'condominium__name',
        )
        assert self.admin.search_fields == expected

    def test_admin_readonly_fields(self):
        expected = ('created_at', 'updated_at')
        assert self.admin.readonly_fields == expected

    def test_admin_list_select_related(self):
        expected = ('bank', 'condominium', 'account_type')
        assert self.admin.list_select_related == expected

    def test_admin_create_via_model(self, admin_user, _bank, _condo, _acc_type):
        account = BankAccount.objects.create(
            bank=_bank, condominium=_condo, account_type=_acc_type,
            initial_balance=Decimal('2500.00'), initial_balance_date='2024-01-01',
            account_name='Conta Principal', agency='1234',
            account_number='12345', account_digit='1',
            is_active=True,
        )
        assert account.pk is not None
        assert BankAccount.objects.count() == 1

    def test_admin_edit_via_model(self, admin_user, _bank, _condo, _acc_type):
        account = BankAccount.objects.create(
            bank=_bank, condominium=_condo, account_type=_acc_type,
            initial_balance_date='2024-01-01', account_name='Conta Original',
            agency='1234', account_number='12345', account_digit='1',
        )
        account.account_name = 'Conta Alterada'
        account.save()
        account.refresh_from_db()
        assert account.account_name == 'Conta Alterada'

    def test_admin_delete_via_model(self, admin_user, _bank, _condo, _acc_type):
        account = BankAccount.objects.create(
            bank=_bank, condominium=_condo, account_type=_acc_type,
            initial_balance_date='2024-01-01', account_name='Conta Deletada',
            agency='1234', account_number='12345', account_digit='1',
        )
        pk = account.pk
        account.delete()
        assert BankAccount.objects.filter(pk=pk).count() == 0
