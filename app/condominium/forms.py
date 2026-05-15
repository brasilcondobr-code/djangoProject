from django import forms
import re
from core.services.hydra_cpf_service import consult_cpf
from .models import Collaborators, Condominium, DocumentCondominium

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
        self.fields['code'].widget.attrs['class'] = 'mask-code'
        self.fields['cnpj'].widget.attrs['class'] = 'mask-cnpj'
         
        
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj and not validate_cnpj(cnpj):
            raise forms.ValidationError('O CNPJ informado é inválido.')
        return cnpj

        
class CollaboratorsFormAdmin(forms.ModelForm):
    class Meta:
        model = Collaborators
        fields = '__all__'
        widgets = {
            'cpf': forms.TextInput(attrs={'class': 'mask-cpf'}),
            'email': forms.EmailInput(attrs={'class': 'mask-email'}),
            'phone_number': forms.TextInput(attrs={'class': 'mask-phone'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'condominium': 'Condomínio',
            'name': 'Nome Completo',
            'cpf': 'CPF',
            'rg': 'RG',
            'email': 'Email',
            'phone_number': 'Telefone',
            'type_collaborator': 'Tipo de Colaborador',
            'photo': 'Foto',
            'is_active': 'Ativo',
            'observations': 'Observações',
        }
        
        help_texts = {
            'condominium': 'Selecione o condomínio do colaborador',
            'name': 'Digite o nome completo do colaborador',
            'cpf': 'Digite o CPF do colaborador',
            'rg': 'Digite o RG do colaborador',
            'email': 'Digite o email do colaborador',
            'phone_number': 'Digite o telefone do colaborador',
            'type_collaborator': 'Selecione o tipo de colaborador',
            'is_active': 'Colaborador ativo',
            'observations': 'Observações adicionais sobre o colaborador',
        }
        
        error_messages = {
            'name': {
                'max_length': 'O nome deve ter no máximo 255 caracteres.',
            },
            'cpf': {
                'max_length': 'O CPF deve ter no máximo 20 caracteres.',
            },
            'rg': {
                'max_length': 'O RG deve ter no máximo 20 caracteres.',
            },
            'email': {
                'max_length': 'O email deve ter no máximo 255 caracteres.',
            },
            'phone_number': {
                'max_length': 'O telefone deve ter no máximo 20 caracteres.',
            },
        }
              
        field_order = [
            'condominium',
            'name',
            'cpf',
            'rg',
            'email',
            'phone_number',
            'type_collaborator',
            'is_active',
            'observations',
            'created_at',
            'updated_at',
        ]
        
        exclude = ['created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super(CollaboratorsFormAdmin, self).__init__(*args, **kwargs)
        self.fields['cpf'].widget.attrs['class'] = 'mask-cpf'
        self.fields['rg'].widget.attrs['class'] = 'mask-rg'
        self.fields['phone_number'].widget.attrs['class'] = 'mask-phone'
        self.fields['email'].widget.attrs['class'] = 'mask-email'

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            if not validate_cpf(cpf):
                raise forms.ValidationError('O CPF informado é inválido.')
            
            # Consultar Receita Federal via HydraCPF se o CPF mudou ou se a situação está vazia
            cpf_digits = "".join(filter(str.isdigit, cpf))
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info(f"Validating CPF for {self.instance}: digits={cpf_digits}")
            
            if not self.instance.pk or self.instance.cpf != cpf or not self.instance.situation:
                logger.info(f"Triggering API consultation for CPF {cpf_digits}")
                result = consult_cpf(cpf_digits)
                logger.info(f"API result for {cpf_digits}: {result}")
                
                if result is not None:
                    self.instance.api_status = 'Pass'
                    if 'error' not in result:
                        self.instance.situation = result.get('situation')
                        self.instance.regular = result.get('regular')
                        self.instance.death = result.get('death')
                        logger.info(f"Updating instance: situation={self.instance.situation}, regular={self.instance.regular}, death={self.instance.death}")
                    else:
                        self.instance.situation = "Erro na Consulta"
                        logger.info("API returned error, setting situation to 'Erro na Consulta'")
                else:
                    self.instance.api_status = 'Fail'
                    logger.info("API result is None, setting api_status to 'Fail'")
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not validate_email(email):
            raise forms.ValidationError('O e-mail informado é inválido.')
        return email
        
class DocumentCondominiumFormAdmin(forms.ModelForm):
    class Meta:
        model = DocumentCondominium
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'condominium': 'Condomínio',
            'name': 'Nome do Documento',
            'file': 'Arquivo do Documento',
            'observations': 'Observações',
            'is_active': 'Ativo',
        }
        
        help_texts = {
            'condominium': 'Selecione o condomínio relacionado ao documento',
            'name': 'Digite o nome do documento',
            'file': 'Selecione o arquivo do documento',
            'observations': 'Observações adicionais sobre o documento',
            'is_active': 'Documento ativo',
        }
        
        error_messages = {
            'condominium': {
                'required': 'O condomínio é obrigatório.',
            },
            'name': {
                'max_length': 'O nome do documento deve ter no máximo 255 caracteres.',
            },
            'file': {
                'required': 'O arquivo do documento é obrigatório.',
            },
            'observations': {
                'max_length': 'As observações do documento devem ter no.maxcdn 255 caracteres.',
            },
            'is_active': {
                'required': 'O campo ativo é obrigatório.',
            },
        }
        
        field_order = [
            'condominium',
            'name',
            'file',
            'observations',
            'is_active',
            'created_at',
            'updated_at',
        ]
        
        exclude = ['created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super(DocumentCondominiumFormAdmin, self).__init__(*args, **kwargs)
        self.fields['condominium'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['observations'].widget.attrs['class'] = 'form-control'
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'