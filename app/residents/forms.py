from django import forms
import re

def validate_cpf(cpf):
    """
    Valida se um CPF é válido.
    """
    cpf = "".join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    def calculate_digit(cpf, weights):
        sum_val = sum(int(digit) * weight for digit, weight in zip(cpf, weights))
        remainder = sum_val % 11
        return 0 if remainder < 2 else 11 - remainder

    weights1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]

    if int(cpf[9]) != calculate_digit(cpf[:9], weights1):
        return False
    if int(cpf[10]) != calculate_digit(cpf[:10], weights2):
        return False

    return True

def validate_cnpj(cnpj):
    """
    Valida se um CNPJ é válido.
    """
    cnpj = "".join(filter(str.isdigit, cnpj))

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    def calculate_digit(cnpj, weights):
        sum_val = sum(int(digit) * weight for digit, weight in zip(cnpj, weights))
        remainder = sum_val % 11
        return 0 if remainder < 2 else 11 - remainder

    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    if int(cnpj[12]) != calculate_digit(cnpj[:12], weights1):
        return False
    if int(cnpj[13]) != calculate_digit(cnpj[:13], weights2):
        return False

    return True

def validate_email(email):
    """
    Valida se um email tem um formato básico válido.
    """
    if not email:
        return True
    
    # Regex simples para validação de email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False
    
    return True

from .models import CondominiumUnit, RealEstateAgency, Vehicle, Visitor

class CondominiumUnitFormAdmin(forms.ModelForm):
    
    class Meta:
        model = CondominiumUnit
        fields = '__all__'
        widgets = {
            'tower': forms.TextInput(attrs={'class': 'mask-tower'}),
            'unit_number': forms.TextInput(attrs={'class': 'mask-unit-number'}),
            'identification': forms.TextInput(attrs={'class': 'mask-identification'}),
            'area_total': forms.NumberInput(attrs={'class': 'mask-area-total'}),
            'sale_price': forms.NumberInput(attrs={'class': 'mask-sale-price'}),
            'rent_price': forms.NumberInput(attrs={'class': 'mask-rent-price'}),
        }
        
        labels = {
            'condominium': 'Condomínio',
            'tower': 'Torre',
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
        self.fields['area_total'].widget.attrs['class'] = 'mask-area-total'
        self.fields['sale_price'].widget.attrs['class'] = 'mask-sale-price'
        self.fields['rent_price'].widget.attrs['class'] = 'mask-rent-price'
    

class ResidentFormAdmin(forms.ModelForm):
    
    class Meta:
        model = CondominiumUnit
        fields = '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'mask-email'}),
            'phone': forms.TextInput(attrs={'class': 'mask-phone'}),
            'cpf': forms.TextInput(attrs={'class': 'mask-cpf'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
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
            'photo': 'Foto',
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
            'photo': 'Selecione uma foto do(a) morador(a)',
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
            'photo': {
                'required': 'A foto é obrigatória.',
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
        self.fields['date_of_birth'].widget.attrs['class'] = 'mask-date-of-birth'

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf and not validate_cpf(cpf):
            raise forms.ValidationError('O CPF informado é inválido.')
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise forms.ValidationError('O e-mail informado é inválido.')
        return email

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            if not (1930 <= dob.year <= 2050):
                raise forms.ValidationError('A data de nascimento deve estar entre os anos 1930 e 2050.')
        return dob
        

class VehicleFormAdmin(forms.ModelForm):
    
    class Meta:
        model = Vehicle
        fields = '__all__'
        widgets = {
            'condo_unit': forms.Select(attrs={'class': 'mask-condo-unit'}),
            'license_plate': forms.TextInput(attrs={'class': 'mask-license-plate'}),
            'year': forms.NumberInput(attrs={'class': 'mask-year'}),
            'garage_space': forms.TextInput(attrs={'class': 'mask-garage-space'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
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
            'photo': 'Foto',
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
        self.fields['condo_unit'].widget.attrs['class'] = 'mask-condo-unit'
        self.fields['license_plate'].widget.attrs['class'] = 'mask-license-plate'
        self.fields['year'].widget.attrs['class'] = 'mask-year'


class VisitorFormAdmin(forms.ModelForm):
    
    class Meta:
        model = Visitor
        fields = '__all__'
        widgets = {
            'condo_unit': forms.Select(attrs={'class': 'mask-condo-unit'}),
            'cpf': forms.TextInput(attrs={'class': 'mask-cpf'}),
            'phone': forms.TextInput(attrs={'class': 'mask-phone'}),
            'visit_date': forms.DateInput(attrs={'class': 'mask-visit-date'}),
        }
        
        labels = {
            'condo_unit': 'Condominio/Unidade',
            'name': 'Nome',
            'cpf': 'CPF',
            'rg': 'RG',
            'phone': 'Telefone',
            'visit_date': 'Data da visita',
            'purpose': 'Proposto da visita',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'condo_unit': 'Selecione a unidade que o visitante irá visitar',
            'name': 'Digite o nome do visitante',
            'cpf': 'Digite o CPF do visitante',
            'rg': 'Digite o RG do visitante',
            'phone': 'Digite o telefone do visitante',
            'visit_date': 'Digite a data da visita',
            'purpose': 'Digite o propósito da visita',
            'is_active': 'Indique se o visitante está ativo',
            'created_at': 'Data de criação do visitante',
            'updated_at': 'Data de atualização do visitante',
        }
        
        error_messages = {
            'condo_unit': {
                'required': 'A unidade é obrigatória.',
                'invalid_choice': 'Selecione uma unidade válida.',
            },
            'name': {
                'required': 'O nome é obrigatório.',
            },
            'cpf': {
                'required': 'O CPF é obrigatório.',
            },
            'rg': {
                'required': 'O RG é obrigatório.',
            },
            'phone': {
                'required': 'O telefone é obrigatório.',
            },
            'visit_date': {
                'required': 'A data da visita é obrigatória.',
            },
            'purpose': {
                'required': 'O propósito da visita é obrigatório.',
            },
            'is_active': {
                'required': 'O status de ativo é obrigatório.',
            },
            'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
             'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            }
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
         
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condo_unit'].widget.attrs['class'] = 'mask-condo-unit'
        self.fields['cpf'].widget.attrs['class'] = 'mask-cpf'
        self.fields['phone'].widget.attrs['class'] = 'mask-phone'
        if 'visit_date' in self.fields:
            self.fields['visit_date'].widget.attrs['class'] = 'mask-visit-date'

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf and not validate_cpf(cpf):
            raise forms.ValidationError('O CPF informado é inválido.')
        return cpf


class RealEstateAgencyFormAdmin(forms.ModelForm):
    
    class Meta:
        model = RealEstateAgency
        fields = '__all__'
        widgets = {
            'condo_unit': forms.Select(attrs={'class': 'mask-condo-unit'}),
            'cnpj': forms.TextInput(attrs={'class': 'mask-cnpj'}),
            'phone': forms.TextInput(attrs={'class': 'mask-phone'}),
            'email': forms.EmailInput(attrs={'class': 'mask-email'}),            
            'website': forms.URLInput(attrs={'class': 'mask-website'}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'condo_unit': 'Condominio/Unidade',
            'name': 'Nome da Imobiliária',
            'trade_name': 'Nome Fantasia',
            'cnpj': 'CNPJ',
            'phone': 'Telefone',
            'email': 'E-mail',
            'website': 'Site',
            'address': 'Endereço',
            'contact_person': 'Pessoa de Contato',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'condo_unit': 'Selecione a unidade associada à imobiliária',
            'name': 'Digite o nome da imobiliária',
            'trade_name': 'Digite o nome fantasia da imobiliária (opcional)',
            'cnpj': 'Digite o CNPJ da imobiliária',
            'phone': 'Digite o telefone da imobiliária',
            'email': 'Digite o e-mail da imobiliária',
            'website': 'Digite o site da imobiliária',
            'address': 'Digite o endereço da imobiliária',
            'contact_person': 'Digite o nome da pessoa de contato na imobiliária',
            'is_active': 'Indique se a imobiliária está ativa',
            'created_at': 'Data de criação da imobiliária',
            'updated_at': 'Data de atualização da imobiliária',
        }
        
        error_messages = {
            'condo_unit': {
                'required': 'A unidade é obrigatória.',
                'invalid_choice': 'Selecione uma unidade válida.',
            },
            'name': {
                'required': 'O nome da imobiliária é obrigatório.',
            },
            'cnpj': {
                'required': 'O CNPJ é obrigatório.',
                'invalid': 'Digite um CNPJ válido.',
            },
            'phone': {
                'required': 'O telefone é obrigatório.',
                'invalid': 'Digite um telefone válido.',
            },
            'email': {
                'required': 'O e-mail é obrigatório.',
                'invalid': 'Digite um e-mail válido.',
            },
            'website': {
                'required': 'O site é obrigatório.',
                'invalid': 'Digite um site válido.',
            },
            'address': {
                'required': 'O endereço é obrigatório.',
            },
            'contact_person': {
                'required': 'A pessoa de contato é obrigatória.',
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
        self.fields['condo_unit'].widget.attrs['class'] = 'mask-condo-unit'
        self.fields['cnpj'].widget.attrs['class'] = 'mask-cnpj'
        self.fields['phone'].widget.attrs['class'] = 'mask-phone'
        self.fields['email'].widget.attrs['class'] = 'mask-email'
        self.fields['website'].widget.attrs['class'] = 'mask-website'

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj and not validate_cnpj(cnpj):
            raise forms.ValidationError('O CNPJ informado é inválido.')
        return cnpj

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not validate_email(email):
            raise forms.ValidationError('O e-mail informado é inválido.')
        return email

    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website:
            # Validação básica: deve começar com http ou https
            if not (website.startswith('http://') or website.startswith('https://')):
                raise forms.ValidationError('O site deve começar com http:// ou https://')
        return website