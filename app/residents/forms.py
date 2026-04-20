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
    

class ResidentFormAdmin(forms.ModelForm):
    
    class Meta:
        model = CondominiumUnit
        fields = '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'mask-email'}),
            'phone': forms.TextInput(attrs={'class': 'mask-phone'}),
            'cpf': forms.TextInput(attrs={'class': 'mask-cpf'}),
        }
        
        labels = {
            'unit': 'Condominio/Unidade',
            'type_of_resident': 'Tipo de Residente',
            'name': 'Nome Completo',
            'email': 'E-mail',
            'phone': 'Número de Telefone',
            'cpf': 'CPF',
            'rg': 'RG',
            'sex': 'Sexo',
            'date_of_birth': 'Data de Nascimento',
            'profission': 'Profissão',
            'is_primary': 'Principal',
            'is_resident': 'Residente',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'unit': 'Selecione a unidade à qual o(a) morador(a) pertence',
            'type_of_resident': 'Selecione o tipo de morador(a)',
            'name': 'Digite o nome completo do(a) morador(a)',
            'email': 'Digite o e-mail do(a) morador(a)',
            'phoner': 'Digite o número de telefone do(a) morador(a)',
            'cpf': 'Digite o CPF do(a) morador(a)',
            'rg': 'Digite o RG do(a) morador(a)',
            'sex': 'Selecione o sexo do(a) morador(a)',
            'date_of_birth': 'Digite a data de nascimento do(a) morador(a)',
            'profission': 'Digite a profissão do(a) morador(a)',
            'is_primary': 'Indique se o(a) morador(a) é o principal da unidade',
            'is_resident': 'Indique se o(a) morador(a) é um morador da unidade',
            'is_active': 'Indique se o(a) morador(a) está ativo',
            'created_at': 'Data de criação do(a) morador(a)',
            'updated_at': 'Data de atualização do(a) morador(a)',
        }
        
        error_messages = {
            'unit': {
                'required': 'A unidade é obrigatória.',
                'invalid_choice': 'Selecione uma unidade válida.',
            },
            'type_of_resident': {
                'required': 'O tipo de morador(a) é obrigatório.',
                'invalid_choice': 'Selecione um tipo de morador(a) válido.',
            },
            'name': {
                'required': 'O nome completo é obrigatório.',
            },
            'email': {
                'required': 'O e-mail é obrigatório.',
                'invalid': 'Digite um e-mail válido.',
            },
            'phone': {
                'required': 'O número de telefone é obrigatório.',
                'invalid': 'Digite um número de telefone válido.',
            },
            'cpf': {
                'required': 'O CPF é obrigatório.',
                'invalid': 'Digite um CPF valido.',
            },
            'rg': {
                'required': 'O RG é obrigatório.',
                'invalid': 'Digite um RG valido.',
            },
            'sex': {
                'required': 'O sexo é obrigatório.',
                'invalid_choice': 'Selecione um sexo valido.',
            },
            'date_of_birth': {
                'required': 'A data de nascimento é obrigatória.',
                'invalid': 'Digite uma data de nascimento valida.',
            },
            'profission': {
                'required': 'A profissão é obrigatória.',
            },
            'is_primary': {
                'required': 'O principal é obrigatório.',
            },
            'is_resident': {
                'required': 'O residente é obrigatório.',
            },
            'is_active': {
                'required': 'O ativo é obrigatório.',
            },
            'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
            'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            },
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'mask-email'
        self.fields['phone'].widget.attrs['class'] = 'mask-phone'
        self.fields['cpf'].widget.attrs['class'] = 'mask-cpf'
        

class VehicleFormAdmin(forms.ModelForm):
    
    class Meta:
        model = CondominiumUnit
        fields = '__all__'
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'mask-license-plate'}),
            'year': forms.NumberInput(attrs={'class': 'mask-year'}),
        }
        
        labels = {
            'condo_unit': 'Condominio/Unidade',
            'vehicle_type': 'Tipo de Veículo',
            'license_plate': 'Placa do Veículo',
            'brand': 'Marca do Veículo',
            'model': 'Modelo do Veículo',
            'color': 'Cor do Veículo',
            'year': 'Ano do Veículo',
            'garage_space': 'Vaga de Garagem',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'condo_unit': 'Selecione a unidade',
            'vehicle_type': 'Selecione o tipo de veículo',
            'license_plate': 'Digite a placa do veículo',
            'brand': 'Digite a marca do veículo',
            'model': 'Digite o modelo do veículo',
            'color': 'Digite a cor do veículo',
            'year': 'Digite o ano do veículo',
            'garage_space': 'Selecione a vaga de garagem associada ao veículo',
            'is_active': 'Indique se o veículo está ativo',
            'created_at': 'Data de criação do veículo',
            'updated_at': 'Data de atualização do veículo',
        }
        
        error_messages = {
            'condo_unit': {
                'required': 'A unidade é obrigatória.',
                'invalid_choice': 'Selecione uma unidade válida.',
            },
            'vehicle_type': {
                'required': 'O tipo de veículo é obrigatório.',
                'invalid_choice': 'Selecione um tipo de veículo válido.',
            },
            'license_plate': {
                'required': 'A placa do veículo é obrigatória.',
            },
            'brand': {
                'required': 'A marca do veículo é obrigatória.',
            },
            'model': {
                'required': 'O modelo do veículo é obrigatório.',
            },
            'color': {
                'required': 'A cor do veículo é obrigatória.',
            },
            'year': {
                'required': 'O ano do veículo é obrigatório.',
                'invalid': 'Digite um ano válido para o veículo.',
            },
            'garage_space': {
                'required': 'A vaga de garagem é obrigatória.',
                'invalid_choice': 'Selecione uma vaga de garagem válida.',
            },
            'is_active': {
                'required': 'O status de ativo é obrigatório.',
            },
            'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
             'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            },
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['license_plate'].widget.attrs['class'] = 'mask-license-plate'
        self.fields['year'].widget.attrs['class'] = 'mask-year'



