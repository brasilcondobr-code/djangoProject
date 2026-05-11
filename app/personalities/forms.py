from django import forms

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

    class Meta:
        model = Entity
        fields = '__all__'
        
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'mask-code form-control',
                'placeholder': 'Código',
                'maxlength': '100',
            }),
            'name': forms.TextInput(attrs={
                'class': 'mask-name form-control',
                'placeholder': 'Nome da Entidade',
                'maxlength': '100',
            }),
            'business_sector': forms.Select(attrs={
                'class': 'mask-business-sector form-control',
            }),
            'kind': forms.Select(attrs={
                'class': 'mask-kind form-control',
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
            'trade_name': forms.TextInput(attrs={
                'class': 'mask-trade-name form-control',
                'placeholder': 'Nome Fantasia',
                'maxlength': '100',
            }),
            'date_of_birth_opening': forms.DateInput(attrs={
                'class': 'mask-date-of-birth-opening form-control',
                'placeholder': 'Data de Nascimento/Abertura',
                'type': 'date',
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
            'name': 'Nome da Entidade',
            'business_sector': 'Ramo de Atividade',
            'kind': 'Tipo',
            'cpf_cnpj': 'CPF/CNPJ',
            'rg_ie': 'RG/IE',
            'municipal_registration': 'Inscrição Municipal',
            'trade_name': 'Nome Fantasia',
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
            'name': 'Digite o nome da entidade',
            'business_sector': 'Selecione o ramo de atividade da entidade',
            'kind': 'Selecione o tipo da entidade',
            'cpf_cnpj': 'Digite o CPF ou CNPJ da entidade',
            'rg_ie': 'Digite o RG ou IE da entidade (opcional)',
            'municipal_registration': 'Digite a inscrição municipal da entidade (opcional)',
            'trade_name': 'Digite o nome fantasia da entidade (opcional)',
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
            'name': {
                'required': 'O nome da entidade é obrigatório.',
            },
            'business_sector': {
                'required': 'O ramo de atividade da entidade é obrigatório.',
            },
            'kind': {
                'required': 'O tipo da entidade é obrigatório.',
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
            'trade_name': {
                'unique': 'Já existe uma entidade com este nome fantasia.',
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
        self.fields['date_of_birth_opening'].widget.attrs.update({
            'class': 'mask-date-of-birth-open form-control',
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