import pytest
from django.db import IntegrityError

from domains.parameters.models.financial_transaction import FinancialTransaction


@pytest.mark.django_db
class TestFinancialTransactionModel:

    def test_create_valid(self):
        transaction = FinancialTransaction.objects.create(
            description='Taxa de condomínio'
        )

        assert transaction.pk is not None
        assert transaction.description == 'Taxa de condomínio'

    def test_default_is_active_true(self):
        transaction = FinancialTransaction.objects.create(
            description='Fundo de reserva'
        )

        assert transaction.is_active is True

    def test_created_at_auto_set(self):
        transaction = FinancialTransaction.objects.create(
            description='Multa por atraso'
        )

        assert transaction.created_at is not None
        assert transaction.updated_at is not None

    def test_updated_at_changes_on_update(self):
        transaction = FinancialTransaction.objects.create(
            description='Operação Original'
        )
        original_updated = transaction.updated_at

        transaction.description = 'Operação Atualizada'
        transaction.save()
        transaction.refresh_from_db()

        assert transaction.updated_at >= original_updated

    def test_str_returns_description(self):
        transaction = FinancialTransaction.objects.create(
            description='Pagamento de fornecedor'
        )

        assert str(transaction) == 'Pagamento de fornecedor'

    def test_duplicate_description_raises(self):
        FinancialTransaction.objects.create(description='Água')
        with pytest.raises(IntegrityError):
            FinancialTransaction.objects.create(description='Água')

    def test_description_required(self):
        with pytest.raises(IntegrityError):
            FinancialTransaction.objects.create(description=None)

    def test_description_max_length(self):
        field = FinancialTransaction._meta.get_field('description')

        assert field.max_length == 255

    def test_description_is_unique(self):
        field = FinancialTransaction._meta.get_field('description')

        assert field.unique is True

    def test_uniqueness_declared_only_once(self):
        assert FinancialTransaction._meta.unique_together == ()
        assert FinancialTransaction._meta.constraints == []

    def test_verbose_names(self):
        assert FinancialTransaction._meta.verbose_name == '30. Operação Financeira'
        assert (
            FinancialTransaction._meta.verbose_name_plural
            == '30. Operações Financeiras'
        )

    def test_db_table_and_ordering(self):
        assert FinancialTransaction._meta.db_table == (
            'parameters_financialtransaction'
        )
        assert FinancialTransaction._meta.ordering == ['description']
