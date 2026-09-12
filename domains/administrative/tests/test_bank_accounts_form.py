import pytest
from decimal import Decimal
from domains.administrative.models import Bank, BankAccount
from domains.administrative.forms import BankAccountForm
from domains.parameters.models import BankAccountType


@pytest.mark.django_db
class TestBankAccountForm:
    def test_form_valid(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank.pk,
            'condominium': _condo.pk,
            'account_type': _acc_type.pk,
            'initial_balance': '2.500,00',
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Principal',
            'agency': '1234',
            'account_number': '12345',
            'account_digit': '1',
            'is_active': True,
        }
        form = BankAccountForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_invalid_without_required(self):
        form = BankAccountForm(data={})
        assert not form.is_valid()
        assert 'bank' in form.errors
        assert 'condominium' in form.errors
        assert 'account_type' in form.errors
        assert 'initial_balance_date' in form.errors
        assert 'account_name' in form.errors
        assert 'agency' in form.errors
        assert 'account_number' in form.errors

    def test_form_invalid_agency_format(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank.pk,
            'condominium': _condo.pk,
            'account_type': _acc_type.pk,
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Teste',
            'agency': '12a45',
            'account_number': '12345',
        }
        form = BankAccountForm(data=data)
        assert not form.is_valid()
        assert 'agency' in form.errors

    def test_form_invalid_account_number_format(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank.pk,
            'condominium': _condo.pk,
            'account_type': _acc_type.pk,
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Teste',
            'agency': '1234',
            'account_number': 'abcdef',
        }
        form = BankAccountForm(data=data)
        assert not form.is_valid()
        assert 'account_number' in form.errors

    def test_form_brazilian_currency_conversion(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank.pk,
            'condominium': _condo.pk,
            'account_type': _acc_type.pk,
            'initial_balance': '2.500,00',
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Teste',
            'agency': '1234',
            'account_number': '12345',
            'account_digit': '1',
        }
        form = BankAccountForm(data=data)
        assert form.is_valid()
        assert form.cleaned_data['initial_balance'] == Decimal('2500.00')

    def test_form_duplicate_validation(self, _bank, _condo, _acc_type):
        BankAccount.objects.create(
            bank=_bank, condominium=_condo, account_type=_acc_type,
            initial_balance_date='2024-01-01', account_name='Conta Existente',
            agency='1234', account_number='11111', account_digit='1',
        )

        data = {
            'bank': _bank.pk,
            'condominium': _condo.pk,
            'account_type': _acc_type.pk,
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Duplicada',
            'agency': '1234',
            'account_number': '22222',
        }
        form = BankAccountForm(data=data)
        assert not form.is_valid()
        assert 'agency' in form.errors

    def test_form_leading_zeros_preserved(self, _bank, _condo, _acc_type):
        data = {
            'bank': _bank.pk,
            'condominium': _condo.pk,
            'account_type': _acc_type.pk,
            'initial_balance_date': '2024-01-01',
            'account_name': 'Conta Teste',
            'agency': '0001',
            'account_number': '00001',
            'account_digit': '1',
        }
        form = BankAccountForm(data=data)
        assert form.is_valid()
        assert form.cleaned_data['agency'] == '0001'
        assert form.cleaned_data['account_number'] == '00001'
