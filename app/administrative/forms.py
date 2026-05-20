from django import forms
from decimal import Decimal, InvalidOperation
from condominium.models import Condominium
from core.services.validators import validate_cpf, validate_phone, validate_iban, validate_date, validate_email
from .models import Bank

class BankForm(forms.ModelForm):
    initial_balance = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'mask-currency'}),
        required=True,
        error_messages={'required': 'O Saldo Inicial é obrigatório.'}
    )

    class Meta:
        model = Bank
        fields = '__all__'
        widgets = {
            'compe': forms.TextInput(attrs={'class': 'mask-compe'}),
            'iban': forms.TextInput(attrs={'class': 'mask-iban', 'placeholder': 'BRXX XXXX XXXX XXXX XXXX XXXX XX'}),
            'agency': forms.TextInput(attrs={'class': 'mask-agency'}),
            'account_number': forms.TextInput(attrs={'class': 'mask-account-number', 'placeholder': '00000'}),
            'account_digit': forms.TextInput(attrs={'class': 'mask-account-digit', 'placeholder': '0'}),
            'cpf_drawn': forms.TextInput(attrs={'class': 'mask-cpf-drawn'}),
            'rg_drawn': forms.TextInput(attrs={'class': 'mask-rg-drawn'}),
            'phone_drawn': forms.TextInput(attrs={'class': 'mask-phone'}),
            'email_drawn': forms.EmailInput(attrs={'class': 'mask-email'}),
            'phone1_manager': forms.TextInput(attrs={'class': 'mask-phone'}),
            'phone2_manager': forms.TextInput(attrs={'class': 'mask-phone'}),
            'phone3_manager': forms.TextInput(attrs={'class': 'mask-phone'}),
            'email_manager': forms.EmailInput(attrs={'class': 'mask-email'}),
        }
        
        labels = {
            'compe': 'Cod Banco',
            'bank_name': 'Nome do Banco',
            'account_type': 'Tipo de Conta',
            'initial_balance': 'Saldo Inicial',
            'initial_balance_date': 'Data do Saldo Inicial',
            'account_name': 'Nome da Conta',
            'iban': 'IBAN',
            'agency': 'Agência',
            'account_number': 'Número da Conta',
            'account_digit': 'Dígito da Conta',
            'bank_address': 'Endereço do Banco',
            'condominium': 'Condomínio',
            'full_name_drawn': 'Nome Completo do Sacado',
            'cpf_drawn': 'CPF do Sacado',
            'rg_drawn': 'RG do Sacado',
            'phone_drawn': 'Telefone do Sacado',
            'email_drawn': 'Email do Sacado',
            'addresses_drawn': 'Endereço do Sacado',
            'full_name_manager': 'Nome Completo do Gerente',
            'phone1_manager': 'Telefone 1 do Gerente',
            'phone2_manager': 'Telefone 2 do Gerente',
            'phone3_manager': 'Telefone 3 do Gerente',
            'email_manager': 'Email do Gerente',
        }
        
        error_messages = {
            'compe': {
                'unique': 'O Código de Compensação informado ja existe.',
            },
            'bank_name': {
                'unique': 'O Nome do Banco informado ja existe.',
            },
             'account_number': {
                'unique': 'O Número da Conta informado ja existe.',
            },
            'account_digit': {
                'unique': 'O Dígito da Conta informado ja existe.',
            },
            'bank_address': {
                'invalid_choice': 'O Endereço do Banco selecionado é inválido.',
            },
            'condominium': {
                'invalid_choice': 'O Condomínio selecionado é inválido.',
            },
            'full_name_drawn': {
                'required': 'O Nome Completo do Sacado é obrigatório.',
            },
            'cpf_drawn': {
                'required': 'O CPF do Sacado é obrigatório.',
            },
            'rg_drawn': {
                'required': 'O RG do Sacado é obrigatório.',
            },
            'phone_drawn': {
                'required': 'O Telefone do Sacado é obrigatório.',
            },
            'email_drawn': {
                'required': 'O Email do Sacado é obrigatório.',
                'invalid': 'O Email do Sacado informado é inválido.',
            },
            'addresses_drawn': {
                'invalid_choice': 'O Endereço do Sacado selecionado é inválido.',
            },
            'full_name_manager': {
                'required': 'O Nome Completo do Gerente é obrigatório.',
            },
            'phone1_manager': {
                'required': 'O Telefone 1 do Gerente é obrigatório.',
            },
            'phone2_manager': {
                'required': 'O Telefone 2 do Gerente é obrigatório.',
            },
            'phone3_manager': {
                'required': 'O Telefone 3 do Gerente é obrigatório.',
            },
            'email_manager': {
                'required': 'O Email do Gerente é obrigatório.',
                'invalid': 'O Email do Gerente informado é inválido.',
            },
        }
        
        exclude = ['created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condominium'].required = True
        self.fields['compe'].widget.attrs['class'] = 'mask-compe'
        self.fields['initial_balance'].widget.attrs['class'] = 'mask-currency'
        self.fields['account_name'].widget.attrs['class'] = 'form-control'
        self.fields['iban'].widget.attrs['class'] = 'mask-iban'
        self.fields['agency'].widget.attrs['class'] = 'mask-agency'
        self.fields['account_number'].widget.attrs['class'] = 'mask-account-number'
        self.fields['account_digit'].widget.attrs['class'] = 'mask-account-digit'
        self.fields['cpf_drawn'].widget.attrs['class'] = 'mask-cpf-drawn'
        self.fields['rg_drawn'].widget.attrs['class'] = 'mask-rg-drawn'
        self.fields['phone_drawn'].widget.attrs['class'] = 'mask-phone'
        self.fields['email_drawn'].widget.attrs['class'] = 'form-control'
        self.fields['phone1_manager'].widget.attrs['class'] = 'mask-phone'
        self.fields['phone2_manager'].widget.attrs['class'] = 'mask-phone'
        self.fields['phone3_manager'].widget.attrs['class'] = 'mask-phone'
        self.fields['email_manager'].widget.attrs['class'] = 'mask-email'

    def clean_iban(self):
        iban = self.cleaned_data.get('iban')
        if iban and not validate_iban(iban):
            raise forms.ValidationError('O formato do IBAN informado é inválido.')
        return iban

    def clean_cpf_drawn(self):
        cpf = self.cleaned_data.get('cpf_drawn')
        if cpf and not validate_cpf(cpf):
            raise forms.ValidationError('O CPF do sacado informado é inválido.')
        return cpf

    def clean_phone_drawn(self):
        phone = self.cleaned_data.get('phone_drawn')
        if phone and not validate_phone(phone):
            raise forms.ValidationError('O telefone do sacado informado é inválido.')
        return phone

    def clean_phone1_manager(self):
        phone = self.cleaned_data.get('phone1_manager')
        if phone and not validate_phone(phone):
            raise forms.ValidationError('O telefone 1 do gerente informado é inválido.')
        return phone

    def clean_phone2_manager(self):
        phone = self.cleaned_data.get('phone2_manager')
        if phone and not validate_phone(phone):
            raise forms.ValidationError('O telefone 2 do gerente informado é inválido.')
        return phone

    def clean_phone3_manager(self):
        phone = self.cleaned_data.get('phone3_manager')
        if phone and not validate_phone(phone):
            raise forms.ValidationError('O telefone 3 do gerente informado é inválido.')
        return phone

    def clean_initial_balance_date(self):
        date_val = self.cleaned_data.get('initial_balance_date')
        if date_val and not validate_date(date_val):
            raise forms.ValidationError('A data do saldo inicial informada é inválida.')
        return date_val

    def clean_initial_balance(self):
        balance_str = self.data.get('initial_balance')
        if not balance_str:
            return self.cleaned_data.get('initial_balance')

        try:
            # Remove thousands separators (.) and replace decimal comma (,) with dot (.)
            clean_value = balance_str.replace('.', '').replace(',', '.')
            balance_decimal = Decimal(clean_value)
            
            if balance_decimal <= Decimal('1.00'):
                raise forms.ValidationError('O saldo inicial deve ser superior a R$ 1,00.')
                
            return balance_decimal
        except (InvalidOperation, ValueError):
            raise forms.ValidationError('Informe um número válido para o saldo inicial.')

    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')
        if account_number and not account_number.isdigit():
            raise forms.ValidationError('O número da conta deve conter apenas números.')
        return account_number

    def clean_account_digit(self):
        account_digit = self.cleaned_data.get('account_digit')
        if account_digit is not None:
            digit_str = str(account_digit)
            if not digit_str.isdigit():
                raise forms.ValidationError('O dígito da conta deve conter apenas números.')
        return account_digit

    def clean_email_drawn(self):
        email = self.cleaned_data.get('email_drawn')
        if email and not validate_email(email):
            raise forms.ValidationError('O email do sacado informado é inválido.')
        return email

    def clean_email_manager(self):
        email = self.cleaned_data.get('email_manager')
        if email and not validate_email(email):
            raise forms.ValidationError('O email do gerente informado é inválido.')
        return email

