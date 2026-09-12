import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal
from domains.administrative.models import Bank, BankAccount
from domains.condominium.models import Condominium
from domains.parameters.models import BankAccountType, States, Addresses, TypesCondominium


@pytest.mark.django_db
class TestBankAccountModel:
    def test_create_bank_account_valid(self, _bank, _condo, _acc_type):
        account = BankAccount.objects.create(
            bank=_bank, condominium=_condo, account_type=_acc_type,
            initial_balance=Decimal('2500.00'), initial_balance_date='2024-01-01',
            account_name='Conta Principal', agency='1234',
            account_number='12345', account_digit='1',
            is_active=True,
        )
        assert account.account_name == 'Conta Principal'
        assert str(account) == 'Conta Principal - Itaú'
        assert account.initial_balance == Decimal('2500.00')

    def test_bank_account_str_without_balance(self, _condo):
        bank = Bank.objects.create(
            compe=104, bank_name='Caixa', is_active=True,
        )
        acc_type = BankAccountType.objects.create(description='Poupança')
        account = BankAccount.objects.create(
            bank=bank, condominium=_condo, account_type=acc_type,
            initial_balance_date='2024-06-01', account_name='Poupança Condomínio',
            agency='0001', account_number='00001', account_digit='1',
        )
        assert str(account) == 'Poupança Condomínio - Caixa'

    def test_bank_account_optional_fields(self, _bank, _condo, _acc_type):
        account = BankAccount.objects.create(
            bank=_bank, condominium=_condo, account_type=_acc_type,
            initial_balance_date='2024-01-01', account_name='Conta Teste',
            agency='1234', account_number='12345', account_digit='1',
        )
        assert account.initial_balance is None
        assert account.is_active is False

    def test_bank_account_required_fields(self):
        with pytest.raises(ValidationError):
            account = BankAccount()
            account.full_clean()

    def test_bank_account_unique_constraint_bank_condominium_type_agency(self, _bank, _condo):
        acc_type = BankAccountType.objects.create(description='Corrente')
        BankAccount.objects.create(
            bank=_bank, condominium=_condo, account_type=acc_type,
            initial_balance_date='2024-01-01', account_name='Conta 1',
            agency='1234', account_number='11111', account_digit='1',
        )
        with pytest.raises(Exception):
            BankAccount.objects.create(
                bank=_bank, condominium=_condo, account_type=acc_type,
                initial_balance_date='2024-01-01', account_name='Conta 2',
                agency='1234', account_number='22222', account_digit='1',
            )

    def test_bank_account_unique_constraint_bank_agency_number(self, _bank, _state):
        addr1 = Addresses.objects.create(
            zip_code='20000-000', street='Rua A', number=1,
            city='Rio de Janeiro', state=_state,
        )
        addr2 = Addresses.objects.create(
            zip_code='20000-001', street='Rua B', number=2,
            city='Rio de Janeiro', state=_state,
        )
        t = TypesCondominium.objects.create(name='Casa')
        condo1 = Condominium.objects.create(
            code='COND002', name='Condo 1', cnpj='22.333.444/0001-72',
            state_registration='111', municipal_registration='222',
            type_condominium=t, address=addr1,
        )
        condo2 = Condominium.objects.create(
            code='COND003', name='Condo 2', cnpj='33.444.555/0001-63',
            state_registration='333', municipal_registration='444',
            type_condominium=t, address=addr2,
        )
        acc_type1 = BankAccountType.objects.create(description='Corrente')
        acc_type2 = BankAccountType.objects.create(description='Poupança')

        BankAccount.objects.create(
            bank=_bank, condominium=condo1, account_type=acc_type1,
            initial_balance_date='2024-01-01', account_name='Conta 1',
            agency='1234', account_number='12345', account_digit='1',
        )
        with pytest.raises(Exception):
            BankAccount.objects.create(
                bank=_bank, condominium=condo2, account_type=acc_type2,
                initial_balance_date='2024-01-01', account_name='Conta 2',
                agency='1234', account_number='12345', account_digit='1',
            )

    def test_bank_account_created_at_updated_at(self, _bank, _condo, _acc_type):
        account = BankAccount.objects.create(
            bank=_bank, condominium=_condo, account_type=_acc_type,
            initial_balance_date='2024-01-01', account_name='Conta Teste',
            agency='1234', account_number='12345', account_digit='1',
        )
        assert account.created_at is not None
        assert account.updated_at is not None
