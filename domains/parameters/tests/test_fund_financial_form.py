import pytest

from domains.parameters.forms import FundFinancialForm
from domains.parameters.models import FundFinancial


def form_data(condominium, **overrides):
    data = {
        'condominium': condominium.pk,
        'description': 'Fundo de Reserva',
        'is_active': 'on',
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestFundFinancialForm:

    def test_form_valid(self, fund_condominium):
        form = FundFinancialForm(data=form_data(fund_condominium))

        assert form.is_valid(), form.errors
        assert form.cleaned_data['description'] == 'Fundo de Reserva'

    def test_condominium_required(self, fund_condominium):
        data = form_data(fund_condominium)
        data.pop('condominium')
        form = FundFinancialForm(data=data)

        assert not form.is_valid()
        assert 'condominium' in form.errors
        assert 'Selecione o condomínio do fundo.' in str(
            form.errors['condominium']
        )

    def test_description_required(self, fund_condominium):
        form = FundFinancialForm(
            data=form_data(fund_condominium, description='')
        )

        assert not form.is_valid()
        assert 'description' in form.errors
        assert 'Informe a descrição do fundo.' in str(
            form.errors['description']
        )

    def test_description_only_spaces(self, fund_condominium):
        form = FundFinancialForm(
            data=form_data(fund_condominium, description='   ')
        )

        assert not form.is_valid()
        assert 'description' in form.errors
        assert 'Informe a descrição do fundo.' in str(
            form.errors['description']
        )

    def test_description_max_length(self, fund_condominium):
        form = FundFinancialForm(
            data=form_data(fund_condominium, description='x' * 256)
        )

        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_is_stripped(self, fund_condominium):
        form = FundFinancialForm(
            data=form_data(fund_condominium, description='  Fundo de Obras  ')
        )

        assert form.is_valid(), form.errors
        assert form.cleaned_data['description'] == 'Fundo de Obras'

    def test_duplicate_description_same_condominium_rejected(
        self, fund_condominium
    ):
        FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )
        form = FundFinancialForm(data=form_data(fund_condominium))

        assert not form.is_valid()
        assert 'description' in form.errors
        assert (
            'Já existe um fundo com esta descrição para o '
            'condomínio selecionado.'
            in str(form.errors['description'])
        )

    def test_duplicate_description_case_insensitive(self, fund_condominium):
        FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )
        form = FundFinancialForm(
            data=form_data(fund_condominium, description='fundo de reserva')
        )

        assert not form.is_valid()
        assert 'description' in form.errors

    def test_same_description_different_condominium_accepted(
        self, fund_condominium, other_condominium
    ):
        FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )
        form = FundFinancialForm(data=form_data(other_condominium))

        assert form.is_valid(), form.errors

    def test_own_description_on_edit(self, fund_condominium):
        fund = FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )
        form = FundFinancialForm(
            instance=fund,
            data=form_data(fund_condominium, description='Fundo de Reserva'),
        )

        assert form.is_valid(), form.errors

    def test_edit_to_description_of_another_record_rejected(
        self, fund_condominium
    ):
        FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )
        fund = FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Obras',
        )
        form = FundFinancialForm(
            instance=fund,
            data=form_data(fund_condominium, description='Fundo de Reserva'),
        )

        assert not form.is_valid()
        assert 'description' in form.errors

    def test_is_active_default_initial(self):
        form = FundFinancialForm()

        assert form.fields['is_active'].initial is True

    def test_fields_exact(self):
        form = FundFinancialForm()

        assert tuple(form.fields) == (
            'condominium',
            'description',
            'is_active',
        )

    def test_widgets_labels_and_help_texts(self):
        form = FundFinancialForm()

        assert form.fields['condominium'].widget.__class__.__name__ == 'Select'
        assert form.fields['description'].widget.attrs['class'] == (
            'form-control'
        )
        assert form.fields['description'].widget.attrs['placeholder'] == (
            'Informe a descrição do fundo'
        )
        assert form.fields['description'].widget.attrs['maxlength'] == '255'
        assert form.fields['is_active'].widget.attrs['class'] == (
            'form-check-input'
        )
        assert form.fields['condominium'].label == 'Condomínio'
        assert form.fields['description'].label == 'Descrição'
        assert form.fields['is_active'].label == 'Ativo'
        assert 'condomínio' in form.fields['condominium'].help_text.lower()
        assert 'unidade' not in form.fields['condominium'].help_text.lower()
        assert 'única' in form.fields['description'].help_text.lower()

    def test_audit_fields_not_exposed(self):
        form = FundFinancialForm()

        assert 'created_at' not in form.fields
        assert 'updated_at' not in form.fields
