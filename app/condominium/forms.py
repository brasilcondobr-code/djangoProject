from django import forms
from .models import Condominium

class CondominiumFormAdmin(forms.ModelForm):
    class Meta:
        model = Condominium
        fields = '__all__'
        widgets = {
            'code': forms.TextInput(attrs={'class': 'mask-code'}),
            'name': forms.TextInput(attrs={'class': 'mask-name'}),
            'cnpj': forms.TextInput(attrs={'class': 'mask-cnpj'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-active'}),
            'state_registration': forms.TextInput(attrs={'class': 'mask-state-registration'}),
            'municipal_registration': forms.TextInput(attrs={'class': 'mask-municipal'}),
            'type_condominium': forms.Select(attrs={'class': 'mask-type-condominium'}),
            'struction_condominium': forms.Select(attrs={'class': 'mask-struction-condominium'}),
            'address': forms.Select(attrs={'class': 'mask-address'}),
        }
        
        labels = {
            'code': 'Código',
            'name': 'Nome do Condomínio',
            'cnpj': 'Nro CNPJ',
            'is_active': 'Ativo',
            'state_registration': 'Inscrição Estadual',
            'municipal_registration': 'Inscrição Municipal',
            'type_condominium': 'Tipo',
            'struction_condominium': 'Tipo de Condomínio',
            'address': 'Endereço',
        }
        
        help_texts = {
            'code': 'Digite o código do condomínio',
            'name': 'Digite o nome do condomínio',
            'cnpj': 'Digite o CNPJ do condomínio',
            'is_active': 'Condomínio ativo',
            'state_registration': 'Digite a inscrição estadual do condomínio',
            'municipal_registration': 'Digite a inscrição municipal do condomínio',
            'type_condominium': 'Selecione o tipo do condomínio',
            'struction_condominium': 'Selecione a estrutura do condomínio',
            'address': 'Endereço do condomínio',
        }
        
        error_messages = {
            'code': {
                'max_length': 'O código deve ter no máximo 100 caracteres.',
            },
            'name': {
                'max_length': 'O nome deve ter no máximo 255 caracteres.',
            },
            'cnpj': {
                'max_length': 'O CNPJ deve ter no máximo 20 caracteres.',
            },
            'state_registration': {
                'max_length': 'A inscrição estadual deve ter no máximo 20 caracteres.',
            },
            'municipal_registration': {
                'max_length': 'A inscrição municipal deve ter no máximo 20 caracteres.',
            },
        }
        
        field_order = [
            'code',
            'name',
            'cnpj',
            'is_active',
            'state_registration',
            'municipal_registration',
            'type_condominium',
            'struction_condominium',
            'address',
            'created_at',
            'updated_at',
        ]
        
        exclude = ['created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super(CondominiumFormAdmin, self).__init__(*args, **kwargs)
        self.fields['cnpj'].widget.attrs['class'] = 'mask-cnpj'
         
        
        