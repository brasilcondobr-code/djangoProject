from django import forms
from core.services.validators import validate_phone, validate_iban, validate_email
from domains.administrative.models import Bank


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = '__all__'
        widgets = {
            'compe': forms.TextInput(attrs={'class': 'mask-compe'}),
            'iban': forms.TextInput(attrs={'class': 'mask-iban', 'placeholder': 'BRXX XXXX XXXX XXXX XXXX XX'}),
            'phone1_manager': forms.TextInput(attrs={'class': 'mask-phone'}),
            'phone2_manager': forms.TextInput(attrs={'class': 'mask-phone'}),
            'phone3_manager': forms.TextInput(attrs={'class': 'mask-phone'}),
            'email_manager': forms.EmailInput(attrs={'class': 'mask-email'}),
        }
        
        labels = {
            'compe': 'Cod Banco',
            'bank_name': 'Nome do Banco',
            'iban': 'IBAN',
            'bank_address': 'Endereço do Banco',
            'is_active': 'Ativo',
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
            'bank_address': {
                'invalid_choice': 'O Endereço do Banco selecionado é inválido.',
            },
        }
        
        exclude = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['compe'].widget.attrs['class'] = 'mask-compe'
        self.fields['iban'].widget.attrs['class'] = 'mask-iban'
        self.fields['phone1_manager'].widget.attrs['class'] = 'mask-phone'
        self.fields['phone2_manager'].widget.attrs['class'] = 'mask-phone'
        self.fields['phone3_manager'].widget.attrs['class'] = 'mask-phone'
        self.fields['email_manager'].widget.attrs['class'] = 'mask-email'

    def clean_iban(self):
        iban = self.cleaned_data.get('iban')
        if iban and not validate_iban(iban):
            raise forms.ValidationError('O formato do IBAN informado é inválido.')
        return iban

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

    def clean_email_manager(self):
        email = self.cleaned_data.get('email_manager')
        if email and not validate_email(email):
            raise forms.ValidationError('O email do gerente informado é inválido.')
        return email
