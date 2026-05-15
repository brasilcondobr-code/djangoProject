from django import forms
from datetime import datetime
from core.services.hydra_cpf_service import consult_cpf
from core.services.validators import validate_cpf, validate_cnpj, validate_email, validate_phone
from .models import BusinessSector, Entity

from core.services.hydra_cpf_service import consult_cpf


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
            
            # Consultar Receita Federal via HydraCPF se o CPF mudou ou se a situação está vazia
            cpf_digits = "".join(filter(str.isdigit, cpf_cnpj))
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info(f"Validating CPF for {self.instance}: digits={cpf_digits}")
            
            if not self.instance.pk or self.instance.cpf_cnpj != cpf_cnpj or not self.instance.situation:
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
        if not email:
            raise forms.ValidationError('O e-mail é obrigatório.')
        if not validate_email(email):
            raise forms.ValidationError('E-mail inválido.')
            
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError('O telefone é obrigatório.')
        if not validate_phone(phone):
            raise forms.ValidationError('Telefone inválido.')
        return phone

    def clean_rg_ie(self):
        rg_ie = self.cleaned_data.get('rg_ie')
        if not rg_ie:
            raise forms.ValidationError('O RG/IE é obrigatório.')
        return rg_ie
