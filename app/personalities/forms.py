from django import forms
import re
from datetime import datetime

def validate_cpf(cpf):
    """
    Valida se um CPF é válido.
    """
    cpf = "".join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
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
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
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
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

from .models import BusinessSector, Entity


class BusinessSectorForm(forms.ModelForm):

    class Meta:
        model = BusinessSector
        fields = '__all__'

        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ramo de Atividade',
                'maxlength': '255',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'id': 'is_active',
                'class': 'form-check-input',
            }),
        }

        labels = {
            'description': 'Ramo de Atividade',
            'is_active': 'Ativo',
        }

        help_texts = {
            'description': 'Digite o ramo de atividade',
            'is_active': 'Indique se o ramo de atividade está ativo',
        }

        error_messages = {
            'description': {
                'required': 'O ramo de atividade é obrigatório.',
            },
        }

    def __init__(self, *args, **kwargs):
        super(BusinessSectorForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({
            'class': 'form-control mask-description',
            'autofocus': True,
        })


    def clean_description(self):
 
        description = (
            self.cleaned_data['description']
            .strip()
        )
 
        if BusinessSector.objects.filter(
            description__iexact=description
        ).exclude(
            pk=self.instance.pk
        ).exists():
 
            raise forms.ValidationError(
                'Já existe um ramo de atividade com este nome.'
            )
 
        return description


class EntityForm(forms.ModelForm):
    date_of_birth_opening = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={
            'class': 'mask-date-of-birth-opening form-control',
            'placeholder': 'DD/MM/AAAA',
        }),
        required=False
    )

    class Meta:
        model = Entity
        fields = '__all__'
        
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'mask-code form-control',
                'placeholder': 'Código',
                'maxlength': '100',
            }),
            'kind': forms.Select(attrs={
                'class': 'mask-kind form-control',
            }),
            'business_sector': forms.Select(attrs={
                'class': 'mask-business-sector form-control',
            }),
            'name': forms.TextInput(attrs={
                'class': 'mask-name form-control',
                'placeholder': 'Nome da Entidade',
                'maxlength': '100',
            }),
            'trade_name': forms.TextInput(attrs={
                'class': 'mask-trade-name form-control',
                'placeholder': 'Nome Fantasia',
                'maxlength': '100',
            }),
            'cpf_cnpj': forms.TextInput(attrs={
                'class': 'mask-cpf-cnpj form-control',
                'placeholder': 'CPF/CNPJ',
                'maxlength': '100',
            }),
            'rg_ie': forms.TextInput(attrs={
                'class': 'mask-rg-ie form-control',
                'placeholder': 'RG/IE',
                'maxlength': '100',
            }),
             'municipal_registration': forms.TextInput(attrs={
                 'class': 'mask-municipal-registration form-control',
                 'placeholder': 'Inscrição Municipal',
                 'maxlength': '100',
             }),
             'sex': forms.Select(attrs={
                 'class': 'mask-sex form-control',
             }),
            'email': forms.EmailInput(attrs={
                'class': 'mask-email form-control',
                'placeholder': 'E-mail',
                'maxlength': '100',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'mask-phone form-control',
                'placeholder': 'Telefone',
                'maxlength': '20',
            }),
            'address': forms.Select(attrs={
                'class': 'mask-address form-control',
            }),
            'observations': forms.Textarea(attrs={
                'class': 'mask-observations form-control',
                'placeholder': 'Observações',
                'rows': 3,  
                'cols': 40,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'id': 'is_active',
                'class': 'form-check-input',   
            }),
            
        }
        
        labels = {
            'code': 'Código',
            'kind': 'Tipo',
            'business_sector': 'Ramo de Atividade',
            'name': 'Nome da Entidade',
            'trade_name': 'Nome Fantasia',
            'cpf_cnpj': 'CPF/CNPJ',
            'rg_ie': 'RG/IE',
            'municipal_registration': 'Inscrição Municipal',
            'date_of_birth_opening': 'Data de Nascimento/Abertura',
            'sex': 'Sexo',
            'email': 'E-mail',
            'phone': 'Telefone',
            'address': 'Endereço',
            'observations': 'Observações',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'code': 'Digite o código da entidade',
            'kind': 'Selecione o tipo da entidade',
            'business_sector': 'Selecione o ramo de atividade da entidade',
            'name': 'Digite o nome da entidade',
            'trade_name': 'Digite o nome fantasia da entidade (opcional)',
            'cpf_cnpj': 'Digite o CPF ou CNPJ da entidade',
            'rg_ie': 'Digite o RG ou IE da entidade (opcional)',
            'municipal_registration': 'Digite a inscrição municipal da entidade (opcional)',
            'date_of_birth_opening': 'Digite a data de nascimento ou abertura da entidade (opcional)',
            'sex': 'Selecione o sexo da entidade',
            'email': 'Digite o e-mail da entidade (opcional)',
            'phone': 'Digite o telefone da entidade (opcional)',
            'address': 'Selecione o endereço da entidade (opcional)',
            'observations': 'Digite observações sobre a entidade (opcional)',
            'is_active': 'Indique se a entidade está ativa',
        }
        
        error_messages = {
            'code': {
                'required': 'O código da entidade é obrigatório.',
                'unique': 'Já existe uma entidade com este código.',
            },
            'kind': {
                'required': 'O tipo da entidade é obrigatório.',
            },
            'business_sector': {
                'required': 'O ramo de atividade da entidade é obrigatório.',
            },
            'name': {
                'required': 'O nome da entidade é obrigatório.',
            },
            'trade_name': {
                'unique': 'Já existe uma entidade com este nome fantasia.',
            },
            'cpf_cnpj': {
                'required': 'O CPF ou CNPJ da entidade é obrigatório.',
                'unique': 'Já existe uma entidade com este CPF ou CNPJ.',
            },
            'rg_ie': {
                'unique': 'Já existe uma entidade com este RG ou IE.',
            },
            'municipal_registration': {
                'unique': 'Já existe uma entidade com esta inscrição municipal.',
            },
            'date_of_birth_opening': {
                'unique': 'Já existe uma entidade com esta data de nascimento ou abertura.',
            },
            'email': {
                'unique': 'Já existe uma entidade com este e-mail.',
            },
            'phone': {
                'unique': 'Já existe uma entidade com este telefone.',
            },
            'address': {
                'unique': 'Já existe uma entidade com este endereço.',
            },
            'observations': {
                'unique': 'Já existe uma entidade com estas observações.',
            },
            'is_active': {
                'required': 'O status da entidade é obrigatório.',
            },
        }
        
    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({
            'class': 'mask-code form-control',
            'autofocus': True,
        })
        self.fields['cpf_cnpj'].widget.attrs.update({
            'class': 'mask-cpf-cnpj form-control',
        })
        self.fields['rg_ie'].widget.attrs.update({
            'class': 'mask-rg-ie form-control',
        })
        self.fields['municipal_registration'].widget.attrs.update({
            'class': 'mask-municipal-registration form-control',
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'mask-phone form-control',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'mask-email form-control',
        })
        self.fields['observations'].widget.attrs.update({
            'class': 'mask-observations form-control',
        })

    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj')
        kind = self.cleaned_data.get('kind')

        if not cpf_cnpj:
            return cpf_cnpj

        if kind == 'PF':
            if not validate_cpf(cpf_cnpj):
                raise forms.ValidationError('CPF inválido.')
        elif kind == 'PJ':
            if not validate_cnpj(cpf_cnpj):
                raise forms.ValidationError('CNPJ inválido.')
        
        return cpf_cnpj

    def clean_date_of_birth_opening(self):
        date_val = self.cleaned_data.get('date_of_birth_opening')
        
        if not date_val:
            return date_val

        # Se já for um objeto date (comportamento padrão do ModelForm para DateField)
        if hasattr(date_val, 'year'):
            date_obj = date_val
        else:
            # Caso seja enviado como string (ex: via API ou widget customizado que não converteu)
            try:
                date_obj = datetime.strptime(date_val, '%d/%m/%Y').date()
            except (ValueError, TypeError):
                raise forms.ValidationError('Data inválida. Use o formato DD/MM/AAAA.')

        if not (1930 <= date_obj.year <= 2050):
            raise forms.ValidationError('A data deve estar entre os anos de 1930 e 2050.')

        return date_val

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if email and not validate_email(email):
            raise forms.ValidationError('E-mail inválido.')
            
        return email