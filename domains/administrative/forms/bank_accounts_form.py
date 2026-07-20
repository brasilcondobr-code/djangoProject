from django import forms
from decimal import Decimal, InvalidOperation
from domains.administrative.models import Bank, BankAccount
from domains.condominium.models import Condominium
from domains.parameters.models import BankAccountType
from domains.administrative.validators import validate_agency, validate_account_number, validate_initial_balance


class BankAccountForm(forms.ModelForm):
    initial_balance = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'mask-currency', 'placeholder': '0,00'}),
        required=False,
        error_messages={'invalid': 'Informe um valor monetário válido.'},
    )

    class Meta:
        model = BankAccount
        fields = '__all__'
        widgets = {
            'agency': forms.TextInput(attrs={
                'class': 'mask-agency',
                'placeholder': 'Ex.: 123456',
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'mask-account-number',
                'placeholder': 'Ex.: 1234567890',
            }),
            'account_digit': forms.TextInput(attrs={
                'class': 'mask-account-digit',
                'placeholder': '0',
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: Conta Principal do Condomínio',
            }),
            'initial_balance_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
        }
        labels = {
            'bank': 'Banco',
            'condominium': 'Condomínio',
            'account_type': 'Tipo de Conta',
            'initial_balance': 'Saldo Inicial',
            'initial_balance_date': 'Data do Saldo Inicial',
            'account_name': 'Nome da Conta',
            'agency': 'Agência',
            'account_number': 'Número da Conta',
            'account_digit': 'Dígito da Conta',
            'is_active': 'Ativo',
        }
        help_texts = {
            'bank': 'Selecione o banco responsável pela conta bancária.',
            'condominium': 'Selecione o condomínio ao qual a conta bancária pertence.',
            'account_type': 'Informe o tipo da conta bancária.',
            'initial_balance': 'Informe o saldo inicial da conta, sem utilizar o símbolo R$.',
            'initial_balance_date': 'Informe a data de referência do saldo inicial.',
            'account_name': 'Informe um nome identificador para a conta bancária.',
            'is_active': 'Indica se a conta está disponível para utilização no sistema.',
        }
        error_messages = {
            'bank': {
                'required': 'Selecione um banco válido.',
                'invalid_choice': 'Selecione um banco válido.',
            },
            'condominium': {
                'required': 'Selecione um condomínio válido.',
                'invalid_choice': 'Selecione um condomínio válido.',
            },
            'account_type': {
                'required': 'Selecione um tipo de conta válido.',
                'invalid_choice': 'Selecione um tipo de conta válido.',
            },
            'initial_balance_date': {
                'required': 'A data do saldo inicial é obrigatória.',
                'invalid': 'Informe uma data válida.',
            },
            'account_name': {
                'required': 'O nome da conta é obrigatório.',
            },
            'agency': {
                'required': 'Informe uma agência válida.',
                'invalid': 'A agência deve conter apenas números.',
            },
            'account_number': {
                'required': 'Informe um número de conta válido.',
                'invalid': 'O número da conta deve conter apenas números.',
            },
            'account_digit': {
                'required': 'Informe o dígito da conta.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank'].queryset = Bank.objects.filter(is_active=True)
        self.fields['account_type'].queryset = BankAccountType.objects.filter(is_active=True)
        self.fields['bank'].widget.attrs['class'] = 'form-control'
        self.fields['condominium'].widget.attrs['class'] = 'form-control'
        self.fields['account_type'].widget.attrs['class'] = 'form-control'
        self.fields['initial_balance'].widget.attrs['class'] = 'mask-currency'
        self.fields['agency'].widget.attrs['class'] = 'mask-agency'
        self.fields['account_number'].widget.attrs['class'] = 'mask-account-number'
        self.fields['account_digit'].widget.attrs['class'] = 'mask-account-digit'

    def clean_account_name(self):
        name = self.cleaned_data.get('account_name')
        if name:
            name = name.strip()
        if not name:
            raise forms.ValidationError('O nome da conta é obrigatório.')
        return name

    def clean_agency(self):
        value = self.cleaned_data.get('agency')
        if value:
            value = value.strip()
        if not value:
            raise forms.ValidationError('Informe uma agência válida.')
        validate_agency(value)
        return value

    def clean_account_number(self):
        value = self.cleaned_data.get('account_number')
        if value:
            value = value.strip()
        if not value:
            raise forms.ValidationError('Informe um número de conta válido.')
        validate_account_number(value)
        return value

    def clean_account_digit(self):
        value = self.cleaned_data.get('account_digit')
        if value:
            value = value.strip()
        if not value:
            raise forms.ValidationError('Informe o dígito da conta.')
        if not value.isdigit():
            raise forms.ValidationError('O dígito da conta deve conter apenas números.')
        return value

    def clean_initial_balance(self):
        balance_str = self.cleaned_data.get('initial_balance')
        if not balance_str:
            return None
        try:
            clean_value = balance_str.replace('.', '').replace(',', '.')
            balance_decimal = Decimal(clean_value)
            validate_initial_balance(balance_decimal)
            return balance_decimal
        except (InvalidOperation, ValueError):
            raise forms.ValidationError('Informe um valor monetário válido.')

    def clean(self):
        cleaned_data = super().clean()
        bank = cleaned_data.get('bank')
        condominium = cleaned_data.get('condominium')
        account_type = cleaned_data.get('account_type')
        agency = cleaned_data.get('agency')
        account_number = cleaned_data.get('account_number')

        if bank and condominium and account_type and agency:
            qs = BankAccount.objects.filter(
                bank=bank,
                condominium=condominium,
                account_type=account_type,
                agency=agency,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('agency', 'Já existe uma conta bancária com esses dados.')

        if bank and agency and account_number:
            qs = BankAccount.objects.filter(
                bank=bank,
                agency=agency,
                account_number=account_number,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('account_number', 'Já existe uma conta bancária com este número de conta para este banco e agência.')

        return cleaned_data
