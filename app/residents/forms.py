from django import forms
from .models import CondominiumUnit

class CondominiumUnitFormAdmin(forms.ModelForm):
    
    class Meta:
        model = CondominiumUnit
        fields = '__all__'
        widgets = {
            'tower': forms.TextInput(attrs={'class': 'mask-tower'}),
            'apartment': forms.TextInput(attrs={'class': 'mask-apartment'}),
            'unit_number': forms.TextInput(attrs={'class': 'mask-unit-number'}),
            'identification': forms.TextInput(attrs={'class': 'mask-identification'}),
            'area_total': forms.NumberInput(attrs={'class': 'mask-area-total'}),
            'sale_price': forms.NumberInput(attrs={'class': 'mask-sale-price'}),
            'rent_price': forms.NumberInput(attrs={'class': 'mask-rent-price'}),
        }
        
        labels = {
            'condominium': 'Condomínio',
            'tower': 'Torre',
            'apartment': 'Apartamento',
            'unit_number': 'Número da Unidade',
            'floor': 'Andar',
            'identification': 'Identificação',
            'unit_type': 'Tipo de Unidade',
            'bedrooms': 'Quartos',
            'bathrooms': 'Banheiros',
            'suites': 'Suítes',
            'garage_spaces': 'Vagas de Garagem',
            'area_total': 'Área Total',
            'status': 'Status',
            'for_sale': 'À Venda',
            'for_rent': 'Para Alugar',
            'sale_price': 'Preço de Venda',
            'rent_price': 'Preço de Aluguel',
            'notes': 'Observações',
        }
        
        help_texts = {
            'condominium': 'Selecione o condomínio ao qual a unidade pertence',
            'tower': 'Digite o bloco ou torre da unidade',
            'unit_number': 'Digite o número da unidade',
            'floor': 'Digite o andar da unidade',
            'identification': 'Digite a identificação da unidade (ex: número do apartamento, letra, etc.)',
            'unit_type': 'Selecione o tipo de unidade',
            'bedrooms': 'Digite o número de quartos',
            'bathrooms': 'Digite o número de banheiros',
            'suites': 'Digite o número de suítes',
            'garage_spaces': 'Digite a quantidade de vagas de garagem',
            'area_total': 'Digite a área total da unidade',
            'status': 'Selecione o status da unidade',
            'for_sale': 'Indique se a unidade está à venda',
            'for_rent': 'Indique se a unidade está para alugar',
            'sale_price': 'Digite o preço de venda da unidade (se aplicável)',
            'rent_price': 'Digite o preço de aluguel da unidade (se aplicável)',
            'notes': 'Digite as observações da unidade',
        }
        
        error_messages = {
            'condominium': {
                'required': 'O condomínio é obrigatório.',
                'invalid_choice': 'Selecione um condomínio válido.',
            },
            'tower': {
                'required': 'O bloco ou torre é obrigatório.',
            },
            'unit_number': {
                'required': 'O número da unidade é obrigatório.',
            },
            'floor': {
                'required': 'O andar é obrigatório.',
            },
            'identification': {
                'required': 'A identificação é obrigatória.',
            },
            'unit_type': {
                'required': 'O tipo de unidade é obrigatório.',
                'invalid_choice': 'Selecione um tipo de unidade válido.',
            },
            'bedrooms': {
                'invalid': 'Digite um número válido de quartos.',
            },
            'bathrooms': {
                'invalid': 'Digite um número válido de banheiros.',
            },
            'suites': {
                'invalid': 'Digite um número válido de suítes.',
            },
            'garage_spaces': {
                'required': 'O número de vagas de garagem é obrigatório.',
                'invalid_choice': 'Selecione um número válido de vagas de garagem.',
            },
             'area_total': {
                'invalid': 'Digite uma área total válida.',
            },
            'status': {
                'required': 'O status é obrigatório.',
                'invalid_choice': 'Selecione um status valido.',
            },
            'for_sale': {
                'required': 'O status é obrigatório.',
                'invalid_choice': 'Selecione um status valido.',
            },
            'for_rent': {
                'required': 'O status é obrigatório.',
                'invalid_choice': 'Selecione um status valido.',
            },
            'sale_price': {
                'invalid': 'Digite um preço de venda válido.',
            },
             'rent_price': {
                'invalid': 'Digite um preço de aluguel válido.',
            },
            'notes': {
                'required': 'As observações da unidade é obrigatória.',
            },
            'created_at': {
                'required': 'A data de criação da unidade é obrigatória.',
            },
            'updated_at': {
                'required': 'A data de atualização da unidade é obrigatória.',
            },
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['identification'].widget.attrs['class'] = 'mask-identification'
    
