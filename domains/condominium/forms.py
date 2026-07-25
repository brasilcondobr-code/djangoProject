from django import forms
from shared.validators import (
    validate_cpf,
    validate_cnpj,
    validate_email,
    validate_phone,
    validate_upload_files_docs,
    validate_date,
)
from domains.condominium.models import Collaborator, Condominium


class CondominiumFormAdmin(forms.ModelForm):

    class Meta:
        model = Condominium
        fields = '__all__'
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'mask-code',
                'placeholder': 'Digite o código do condomínio',
            }),
            'name': forms.TextInput(attrs={
                'class': 'mask-name',
                'placeholder': 'Digite o nome do condomínio',
            }),
            'cnpj': forms.TextInput(attrs={
                'class': 'mask-cnpj',
                'placeholder': '00.000.000/0000-00',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'mask-active',
            }),
            'state_registration': forms.TextInput(attrs={
                'class': 'mask-state-registration',
                'placeholder': 'Digite a inscrição estadual',
            }),
            'municipal_registration': forms.TextInput(attrs={
                'class': 'mask-municipal',
                'placeholder': 'Digite a inscrição municipal',
            }),
            'type_condominium': forms.Select(attrs={
                'class': 'mask-type-condominium form-control',
            }),
            'struction_condominium': forms.Select(attrs={
                'class': 'mask-struction-condominium form-control',
            }),
            'address': forms.Select(attrs={
                'class': 'mask-address form-control select2',
            }),
        }

        labels = {
            'code': 'Código',
            'name': 'Nome do Condomínio',
            'cnpj': 'Nro CNPJ',
            'is_active': 'Ativo',
            'state_registration': 'Inscrição Estadual',
            'municipal_registration': 'Inscrição Municipal',
            'type_condominium': 'Tipo',
            'struction_condominium': 'Tipo de Condomínio',
            'address': 'Endereço',
        }

        help_texts = {
            'code': 'Código identificador único do condomínio.',
            'name': 'Nome completo do condomínio conforme registro.',
            'cnpj': 'CNPJ do condomínio com 14 dígitos.',
            'is_active': 'Indica se o condomínio está ativo no sistema.',
            'state_registration': 'Inscrição estadual do condomínio (se aplicável).',
            'municipal_registration': 'Inscrição municipal do condomínio (se aplicável).',
            'type_condominium': 'Selecione a classificação do tipo de condomínio.',
            'struction_condominium': 'Selecione a estrutura física do condomínio.',
            'address': 'Endereço cadastrado do condomínio.',
        }

        error_messages = {
            'code': {
                'max_length': 'O código deve ter no máximo 100 caracteres.',
                'required': 'O código é obrigatório.',
                'unique': 'Já existe um condomínio com este código.',
            },
            'name': {
                'max_length': 'O nome deve ter no máximo 255 caracteres.',
                'required': 'O nome é obrigatório.',
            },
            'cnpj': {
                'max_length': 'O CNPJ deve ter no máximo 20 caracteres.',
                'required': 'O CNPJ é obrigatório.',
                'unique': 'Já existe um condomínio com este CNPJ.',
            },
            'state_registration': {
                'max_length': 'A inscrição estadual deve ter no máximo 20 caracteres.',
            },
            'municipal_registration': {
                'max_length': 'A inscrição municipal deve ter no máximo 20 caracteres.',
            },
            'type_condominium': {
                'required': 'O tipo de condomínio é obrigatório.',
            },
            'address': {
                'required': 'O endereço é obrigatório.',
            },
        }

        exclude = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            if isinstance(field.widget, forms.TextInput):
                if not field.widget.attrs.get('placeholder'):
                    field.widget.attrs['placeholder'] = field.label or field_name

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj and not validate_cnpj(cnpj):
            raise forms.ValidationError('O CNPJ informado é inválido.')
        return cnpj


class CollaboratorsFormAdmin(forms.ModelForm):

    class Meta:
        model = Collaborator
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mask-name',
                'placeholder': 'Digite o nome completo',
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'mask-cpf',
                'placeholder': '000.000.000-00',
            }),
            'rg': forms.TextInput(attrs={
                'class': 'mask-rg',
                'placeholder': 'Digite o RG',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mask-email',
                'placeholder': 'email@exemplo.com',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'mask-phone',
                'placeholder': '(00) 00000-0000',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'certificate_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'certificate_presentation_date': forms.DateInput(attrs={
                'class': 'mask-date',
                'placeholder': 'dd/mm/aaaa',
            }),
            'certificate_validity': forms.DateInput(attrs={
                'class': 'mask-date',
                'placeholder': 'dd/mm/aaaa',
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observações adicionais sobre o colaborador',
                'rows': 3,
            }),
            'observations_certificate': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observações sobre a certidão',
                'rows': 3,
            }),
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
            'certificate_presentation_date': 'Data de Apresentação da Certidão',
            'certificate_validity': 'Validade da Certidão',
            'observations_certificate': 'Observações da Certidão',
            'certificate_file': 'Arquivo da Certidão',
        }

        help_texts = {
            'condominium': 'Selecione o condomínio ao qual o colaborador está vinculado.',
            'name': 'Nome completo do colaborador sem abreviações.',
            'cpf': 'CPF com 11 dígitos numéricos.',
            'rg': 'RG com número e órgão emissor.',
            'email': 'E-mail corporativo ou pessoal do colaborador.',
            'phone_number': 'Telefone com DDD (fixo ou celular).',
            'type_collaborator': 'Selecione a função/cargo do colaborador.',
            'photo': 'Foto recente do colaborador (formatos JPG/PNG).',
            'is_active': 'Colaborador ativo no sistema.',
            'observations': 'Informações complementares sobre o colaborador.',
            'certificate_presentation_date': 'Data em que a certidão foi apresentada.',
            'certificate_validity': 'Data de validade da certidão apresentada.',
            'observations_certificate': 'Anotações relevantes sobre a certidão.',
            'certificate_file': 'Arquivo digital da certidão (PDF, JPG, PNG).',
        }

        error_messages = {
            'name': {
                'max_length': 'O nome deve ter no máximo 255 caracteres.',
                'required': 'O nome é obrigatório.',
            },
            'cpf': {
                'max_length': 'O CPF deve ter no máximo 20 caracteres.',
                'required': 'O CPF é obrigatório.',
                'unique': 'Já existe um colaborador com este CPF.',
            },
            'rg': {
                'max_length': 'O RG deve ter no máximo 20 caracteres.',
                'required': 'O RG é obrigatório.',
            },
            'email': {
                'max_length': 'O email deve ter no máximo 255 caracteres.',
                'required': 'O email é obrigatório.',
                'unique': 'Já existe um colaborador com este email.',
            },
            'phone_number': {
                'max_length': 'O telefone deve ter no máximo 20 caracteres.',
                'required': 'O telefone é obrigatório.',
            },
            'condominium': {
                'required': 'O condomínio é obrigatório.',
            },
        }

        exclude = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cpf'].widget.attrs['class'] = 'mask-cpf'
        self.fields['rg'].widget.attrs['class'] = 'mask-rg'
        self.fields['phone_number'].widget.attrs['class'] = 'mask-phone'
        self.fields['email'].widget.attrs['class'] = 'mask-email'
        if 'certificate_file' in self.fields:
            self.fields['certificate_file'].validators.append(validate_upload_files_docs)

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            if not validate_cpf(cpf):
                raise forms.ValidationError('O CPF informado é inválido.')
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not validate_email(email):
            raise forms.ValidationError('O e-mail informado é inválido.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not validate_phone(phone):
            raise forms.ValidationError('O telefone informado é inválido.')
        return phone

    def clean_certificate_presentation_date(self):
        date_val = self.cleaned_data.get('certificate_presentation_date')
        if date_val and not validate_date(date_val):
            raise forms.ValidationError('A data de apresentação da certidão é inválida.')
        return date_val

    def clean_certificate_validity(self):
        date_val = self.cleaned_data.get('certificate_validity')
        if date_val and not validate_date(date_val):
            raise forms.ValidationError('A data de validade da certidão é inválida.')
        return date_val
