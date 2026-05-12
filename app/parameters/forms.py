from django import forms
from .models import Addresses, States


class StatesForm(forms.ModelForm):
    class Meta:
        model = States
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mask-name'}),
            'abbreviation': forms.TextInput(attrs={'class': 'mask-abbreviation'}),
            'capital': forms.TextInput(attrs={'class': 'mask-capital'}),
            'region': forms.Select(attrs={'class': 'mask-region'}),
        }
        labels = {
            'name': 'Nome do Estado',
            'abbreviation': 'Abreviação (UF)',
            'capital': 'Capital',
            'region': 'Região',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'name': 'Digite o nome do estado',
            'abbreviation': 'Digite a abreviação do estado',
            'capital': 'Digite o nome da capital do estado',
            'region': 'Selecione a região do estado',
            'created_at': 'Data de criação do estado',
            'updated_at': 'Data de atualização do estado',
        }
        
        error_messages = {
            'name': {
                'required': 'O nome do estado é obrigatório.',
            },
            'abbreviation': {
                'required': 'A abreviação do estado é obrigatória.',
            },
            'capital': {
                'required': 'A capital do estado é obrigatória.',
            },
            'region': {
                'required': 'A região do estado é obrigatória.',
            },
            'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
            'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            },
        }
        
    def __init__(self, *args, **kwargs):
        super(StatesForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'mask-name'
        self.fields['abbreviation'].widget.attrs['class'] = 'mask-abbreviation'
        self.fields['capital'].widget.attrs['class'] = 'mask-capital'
        self.fields['region'].widget.attrs['class'] = 'mask-region'
        
        

class AddressesForm(forms.ModelForm):
    class Meta:
        model = Addresses
        fields = '__all__'
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is-active'}),
            'zip_code': forms.TextInput(attrs={'class': 'mask-zip-code'}),
            'street': forms.TextInput(attrs={'class': 'mask-street'}),
            'number': forms.TextInput(attrs={'class': 'mask-number', 'placeholder': '000000'}),
            'complement': forms.TextInput(attrs={'class': 'mask-complement'}),
            'neighborhood': forms.TextInput(attrs={'class': 'mask-neighborhood'}),
            'city': forms.TextInput(attrs={'class': 'mask-city'}),
            'state': forms.Select(attrs={'class': 'mask-state'}),
            'country': forms.TextInput(attrs={'class': 'mask-country'}),
        }
        
        labels = {
            'is_active': 'Ativo',
            'zip_code': 'CEP',
            'street': 'Logradouro',
            'number': 'Número',
            'complement': 'Complemento',
            'neighborhood': 'Bairro',
            'city': 'Município',
            'state': 'UF',
            'country': 'País',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'is_active': 'Indique se o endereço está ativo',
            'zip_code': 'Digite o código postal do endereço',
            'street': 'Digite o logradouro do endereço',
            'number': 'Digite o número do endereço',
            'complement': 'Digite o complemento do endereço',
            'neighborhood': 'Digite o bairro do endereço',
            'city': 'Selecione a cidade do endereço',
            'state': 'Selecione o estado do endereço',
            'country': 'Selecione o país do endereço',
            'created_at': 'Data de criação do endereço',
            'updated_at': 'Data de atualização do endereço',
        }
        
        error_messages = {
            'is_active': {
                'required': 'O campo Ativo é obrigatório.',
            },
            'zip_code': {
                'required': 'O código postal é obrigatório.',
            },
            'street': {
                'required': 'O logradouro é obrigatório.',
            },
            'number': {
                'required': 'O número é obrigatório.',
                'invalid': 'Digite um número válido.',
            },
            'complement': {
                'required': 'O complemento é obrigatório.',
            },
            'neighborhood': {
                'required': 'O bairro é obrigatório.',
            },
            'city': {
                'required': 'A cidade é obrigatória.',
            },
            'state': {
                'required': 'O estado é obrigatório.',
            },
            'country': {
                'required': 'O país é obrigatório.',
            },
            'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
            'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            },
        }
        
    def clean_number(self):
        number = self.cleaned_data.get('number')
        
        # Se o campo for IntegerField, o 'number' já virá como int.
        # Se for CharField, virá como string.
        # Convertemos para string para garantir que a validação funcione.
        str_number = str(number)

        if not str_number.isdigit():
            raise forms.ValidationError("O número deve conter apenas dígitos.")
        
        return number
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zip_code'].widget.attrs['class'] = 'mask-zip-code'
        self.fields['street'].widget.attrs['class'] = 'mask-street'
        self.fields['number'].widget.attrs['class'] = 'mask-number'
        self.fields['complement'].widget.attrs['class'] = 'mask-complement'
        self.fields['neighborhood'].widget.attrs['class'] = 'mask-neighborhood'
        self.fields['city'].widget.attrs['class'] = 'mask-city'
        self.fields['state'].widget.attrs['class'] = 'mask-state'
        self.fields['country'].widget.attrs['class'] = 'mask-country'

