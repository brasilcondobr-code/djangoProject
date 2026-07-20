import pytest
from decimal import Decimal
from django.db import IntegrityError
from domains.administrative.models import Bank, BankAccount
from domains.administrative.services import BankAccountService
from domains.parameters.models import BankAccountType


@pytest.mark.django_db
class TestBankAccountService:
    def test_create_bank_account(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank,
            'condominium': _condo,
            'account_type': _acc_type,
            'initial_balance': Decimal('2500.00'),
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Principal',
            'agency': '1234',
            'account_number': '12345',
            'is_active': True,
        }
        account = BankAccountService.create_bank_account(data)
        assert account.pk is not None
        assert account.account_name == 'Conta Principal'

    def test_create_bank_account_duplicate_raises_error(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank,
            'condominium': _condo,
            'account_type': _acc_type,
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Original',
            'agency': '1234',
            'account_number': '11111',
        }
        BankAccountService.create_bank_account(data)

        with pytest.raises(IntegrityError):
            BankAccountService.create_bank_account(data)

    def test_update_bank_account(self, _bank, _condo, _acc_type):
        data_create = {
            'bank': _bank,
            'condominium': _condo,
            'account_type': _acc_type,
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Original',
            'agency': '1234',
            'account_number': '12345',
        }
        account = BankAccountService.create_bank_account(data_create)

        data_update = {
            'account_name': 'Conta Alterada',
            'initial_balance': Decimal('5000.00'),
        }
        updated = BankAccountService.update_bank_account(account.pk, data_update)
        assert updated is not None
        assert updated.account_name == 'Conta Alterada'
        assert updated.initial_balance == Decimal('5000.00')

    def test_update_nonexistent_account_returns_none(self):
        result = BankAccountService.update_bank_account(99999, {'account_name': 'Teste'})
        assert result is None

    def test_delete_bank_account(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank,
            'condominium': _condo,
            'account_type': _acc_type,
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Deletada',
            'agency': '1234',
            'account_number': '12345',
        }
        account = BankAccountService.create_bank_account(data)
        pk = account.pk

        result = BankAccountService.delete_bank_account(pk)
        assert result is True
        assert BankAccount.objects.filter(pk=pk).count() == 0

    def test_delete_nonexistent_account_returns_false(self):
        result = BankAccountService.delete_bank_account(99999)
        assert result is False

    def test_get_all_bank_accounts(self, _bank, _condo):
        acc_type1 = BankAccountType.objects.create(description='Corrente')
        acc_type2 = BankAccountType.objects.create(description='Poupança')
        BankAccountService.create_bank_account({
            'bank': _bank, 'condominium': _condo, 'account_type': acc_type1,
            'initial_balance_date': '2024-01-01', 'account_name': 'Conta 1',
            'agency': '1234', 'account_number': '11111',
        })
        BankAccountService.create_bank_account({
            'bank': _bank, 'condominium': _condo, 'account_type': acc_type2,
            'initial_balance_date': '2024-01-01', 'account_name': 'Conta 2',
            'agency': '1234', 'account_number': '22222',
        })

        accounts = BankAccountService.get_all_bank_accounts()
        assert len(accounts) == 2

    def test_get_bank_account_by_id(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank, 'condominium': _condo, 'account_type': _acc_type,
            'initial_balance_date': '2024-01-01', 'account_name': 'Conta Teste',
            'agency': '1234', 'account_number': '12345',
        }
        account = BankAccountService.create_bank_account(data)

        found = BankAccountService.get_bank_account_by_id(account.pk)
        assert found is not None
        assert found.account_name == 'Conta Teste'

    def test_get_bank_account_by_id_not_found(self):
        result = BankAccountService.get_bank_account_by_id(99999)
        assert result is None
