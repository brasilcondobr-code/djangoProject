import pytest

from domains.parameters.forms import FinancialTransactionForm
from domains.parameters.models.financial_transaction import FinancialTransaction


@pytest.mark.django_db
class TestFinancialTransactionForm:

    def test_form_valid(self):
        form = FinancialTransactionForm(data={'description': 'Taxa de condomínio'})

        assert form.is_valid(), form.errors

    def test_description_required(self):
        form = FinancialTransactionForm(data={'description': ''})

        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_spaces(self):
        form = FinancialTransactionForm(data={'description': '   '})

        assert not form.is_valid()
        assert 'description' in form.errors

    def test_duplicate_description(self):
        FinancialTransaction.objects.create(description='Água')

        form = FinancialTransactionForm(data={'description': 'Água'})

        assert not form.is_valid()
        assert 'description' in form.errors
        assert 'Já existe uma operação financeira' in str(
            form.errors['description']
        )

    def test_duplicate_description_case_insensitive(self):
        FinancialTransaction.objects.create(description='Taxa de Condomínio')

        form = FinancialTransactionForm(data={'description': 'taxa de condomínio'})

        assert not form.is_valid()
        assert 'description' in form.errors

    def test_whitespace_normalized(self):
        form = FinancialTransactionForm(data={'description': '  Gás  '})

        assert form.is_valid(), form.errors
        assert form.cleaned_data['description'] == 'Gás'

    def test_own_description_on_edit(self):
        transaction = FinancialTransaction.objects.create(description='Energia')

        form = FinancialTransactionForm(
            instance=transaction,
            data={'description': 'Energia  '},
        )

        assert form.is_valid(), form.errors

    def test_is_active_default(self):
        form = FinancialTransactionForm()

        assert form.fields['is_active'].initial is True

    def test_automatic_fields_are_not_editable(self):
        form = FinancialTransactionForm()

        assert 'created_at' not in form.fields
        assert 'updated_at' not in form.fields

    def test_automatic_fields_ignored_on_submit(self):
        form = FinancialTransactionForm(data={
            'description': 'Seguro',
            'created_at': '2000-01-01 00:00:00',
            'updated_at': '2000-01-01 00:00:00',
        })

        assert form.is_valid(), form.errors
        transaction = form.save()

        assert transaction.created_at.year != 2000
        assert transaction.updated_at.year != 2000

    def test_labels(self):
        form = FinancialTransactionForm()

        assert form.fields['description'].label == 'Descrição'
        assert form.fields['is_active'].label == 'Ativo'

    def test_error_messages(self):
        form = FinancialTransactionForm(data={'description': ''})

        assert not form.is_valid()
        assert 'Informe a descrição' in str(form.errors['description'])

    def test_widgets(self):
        form = FinancialTransactionForm()

        assert form.fields['description'].widget.attrs.get('placeholder') is not None
        assert form.fields['description'].widget.attrs.get('maxlength') == '255'
