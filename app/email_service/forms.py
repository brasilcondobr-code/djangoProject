from django import forms
from django.core.exceptions import ValidationError
from .models import ConnectionStatus, TypesProvider, SMTPConfiguration

class TypesProviderForm(forms.ModelForm):
    class Meta:
        model = TypesProvider
        fields = '__all__'
        widgets = {
            'provider': forms.TextInput(attrs={'class': 'mask-provider'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is_active'}),
        }
        
        labels = {
            'provider': 'Fornecedor',
            'is_active': 'Ativo',
        }
        
        help_texts = {
            'provider': 'Digite o fornecedor',
            'is_active': 'Fornecedor ativo',
        }
        
        error_messages = {
            'provider': {
                'max_length': 'O fornecedor deve ter no.maxcdn 255 caracteres.',
            },
            'is_active': {
                'invalid': 'Selecione uma opção válida.',
            },
        }
    
    def clean_provider(self):
        provider = self.cleaned_data.get('provider')
        if not provider:
            raise forms.ValidationError('O fornecedor é obrigatório.')
        if len(provider) > 255:
            raise forms.ValidationError('O fornecedor deve ter no.maxcdn 255 caracteres.')
        return provider
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provider'].widget.attrs['class'] = 'mask-provider'
        self.fields['is_active'].widget.attrs['class'] = 'mask-is_active'


class ConnectionStatusForm(forms.ModelForm):
    class Meta:
        model = ConnectionStatus
        fields = '__all__'
        widgets = {
            'status': forms.TextInput(attrs={'class': 'mask-status'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is_active'}),
        }
        
        labels = {
            'status': 'Status de Conexão',
            'is_active': 'Ativo',
        }
        
        help_texts = {
            'status': 'Digite o status de conexão',
            'is_active': 'Status de conexão ativo',
        }
        
        error_messages = {
            'status': {
                'max_length': 'O status de conexão deve ter no.maxcdn 255 caracteres.',
            },
            'is_active': {
                'invalid': 'Selecione uma opção válida.',
            },
        }
    
    def clean_status(self):
        status = self.cleaned_data.get('status')
        if not status:
            raise forms.ValidationError('O status de conexão é obrigatório.')
        if len(status) > 255:
            raise forms.ValidationError('O status de conexão deve ter no máximo 255 caracteres.')
        return status
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'mask-status'
        self.fields['is_active'].widget.attrs['class'] = 'mask-is_active'


class SMTPConfigurationForm(forms.ModelForm):
    class Meta:
        model = SMTPConfiguration
        fields = '__all__'
        widgets = {
            'description': forms.TextInput(attrs={'class': 'mask-description', 'placeholder': 'Ex: Gmail Principal'}),
            'provider_code': forms.TextInput(attrs={'class': 'mask-provider_code', 'placeholder': 'Ex: GMAIL_01'}),
            'provider_type': forms.Select(),
            'smtp_host': forms.TextInput(attrs={'class': 'mask-smtp_host', 'placeholder': 'smtp.gmail.com'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'mask-smtp_port', 'placeholder': '587'}),
            'username': forms.TextInput(attrs={'class': 'mask-username', 'placeholder': 'usuario@email.com'}),
            'password': forms.PasswordInput(attrs={'class': 'mask-password'}),
            'use_tls': forms.Select(),
            'use_ssl': forms.Select(),
            'smtp_authentication': forms.Select(),
            'api_supported': forms.Select(),
            'is_default': forms.CheckboxInput(),
            'is_active': forms.CheckboxInput(),
            'api_url': forms.URLInput(attrs={'class': 'mask-api_url', 'placeholder': 'https://api.provider.com'}),
            'api_key': forms.TextInput(attrs={'class': 'mask-api_key'}),
            'api_secret': forms.PasswordInput(attrs={'class': 'mask-api_secret'}),
            'api_version': forms.TextInput(attrs={'class': 'mask-api_version'}),
            'emails_per_hour': forms.NumberInput(attrs={'class': 'mask-number'}),
            'emails_per_day': forms.NumberInput(attrs={'class': 'mask-number'}),
            'max_recipients_per_email': forms.NumberInput(attrs={'class': 'mask-number'}),
            'test_email_address': forms.EmailInput(attrs={'class': 'mask-email'}),
            'last_connection_tested_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'connection_status': forms.Select(),
        }
        
        labels = {
            'description': 'Descrição',
            'provider_code': 'Código do Provedor',
            'provider_type': 'Tipo de Provedor',
            'smtp_host': 'Host SMTP',
            'smtp_port': 'Porta SMTP',
            'username': 'Nome de Usuário',
            'password': 'Senha',
            'use_tls': 'Utilizar TLS',
            'use_ssl': 'Utilizar SSL',
            'smtp_authentication': 'Requer autenticação SMTP',
            'api_supported': 'Suporta API',
            'is_default': 'Padrão',
            'is_active': 'Ativo',
            'api_url': 'URL API',
            'api_key': 'Chave API',
            'api_secret': 'Segredo API',
            'api_version': 'Versão API',
            'emails_per_hour': 'Limite por hora',
            'emails_per_day': 'Limite por dia',
            'max_recipients_per_email': 'Máximo destinatários',
            'test_email_address': 'E-mail para testes',
            'last_connection_tested_at': 'Último teste',
            'connection_status': 'Status conexão',
        }

        help_texts = {
            'description': 'Descrição curta para identificação do provedor.',
            'provider_code': 'Código único do provedor para integração.',
            'smtp_host': 'Endereço do servidor SMTP.',
            'smtp_port': 'Porta de conexão do servidor SMTP.',
            'test_email_address': 'E-mail utilizado para validar a conexão.',
        }

    def clean(self):
        cleaned_data = super().clean()
        
        use_tls = cleaned_data.get('use_tls')
        use_ssl = cleaned_data.get('use_ssl')
        smtp_authentication = cleaned_data.get('smtp_authentication')
        api_supported = cleaned_data.get('api_supported')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        api_url = cleaned_data.get('api_url')
        api_key = cleaned_data.get('api_key')
        api_secret = cleaned_data.get('api_secret')
        api_version = cleaned_data.get('api_version')

        # RN005: Não permitir SSL e TLS simultaneamente
        if use_tls and use_ssl:
            raise ValidationError('Não permitir SSL e TLS simultaneamente.')

        # RN004: Se smtp_authentication = True, então username e password obrigatórios
        if smtp_authentication:
            if not username:
                self.add_error('username', 'O nome de usuário é obrigatório quando a autenticação SMTP está ativa.')
            if not password:
                self.add_error('password', 'A senha é obrigatória quando a autenticação SMTP está ativa.')

        # RN003: Se api_supported = False, então campos API não são obrigatórios (implicitly handled by blank=True)
        # If api_supported is True, we might want them to be required.
        if api_supported:
            if not api_url:
                self.add_error('api_url', 'A URL da API é obrigatória quando o suporte a API está ativo.')
            if not api_key:
                self.add_error('api_key', 'A chave da API é obrigatória quando o suporte a API está ativo.')

        return cleaned_data



class ConnectionStatusForm(forms.ModelForm):
    class Meta:
        model = ConnectionStatus
        fields = '__all__'
        widgets = {
            'status': forms.TextInput(attrs={'class': 'mask-status'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is_active'}),
        }
        
        labels = {
            'status': 'Status de Conexão',
            'is_active': 'Ativo',
        }
        
        help_texts = {
            'status': 'Digite o status de conexão',
            'is_active': 'Status de conexão ativo',
        }
        
        error_messages = {
            'status': {
                'max_length': 'O status de conexão deve ter no.maxcdn 255 caracteres.',
            },
            'is_active': {
                'invalid': 'Selecione uma opção válida.',
            },
        }
    
    def clean_status(self):
        status = self.cleaned_data.get('status')
        if not status:
            raise forms.ValidationError('O status de conexão é obrigatório.')
        if len(status) > 255:
            raise forms.ValidationError('O status de conexão deve ter no máximo 255 caracteres.')
        return status
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'mask-status'
        self.fields['is_active'].widget.attrs['class'] = 'mask-is_active'


class EmailProviderForm(forms.ModelForm):
    class Meta:
        model = TypesProvider
        fields = '__all__'
        widgets = {
            'description': forms.TextInput(attrs={'class': 'mask-description'}),
            'provider_code': forms.TextInput(attrs={'class': 'mask-provider_code'}),
            'provider_type': forms.Select(attrs={'class': 'mask-provider_type'}),
            'smtp_host': forms.TextInput(attrs={'class': 'mask-smtp_host'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'mask-smtp_port'}),
            'username': forms.TextInput(attrs={'class': 'mask-username'}),
            'password': forms.TextInput(attrs={'class': 'mask-password'}),
            'use_tls': forms.CheckboxInput(attrs={'class': 'mask-use_tls'}),
            'use_ssl': forms.CheckboxInput(attrs={'class': 'mask-use_ssl'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is_active'}),
            'smtp_authentication': forms.CheckboxInput(attrs={'class': 'mask-smtp_authentication'}),
            'api_supported': forms.CheckboxInput(attrs={'class': 'mask-api_supported'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'mask-is_default'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is_active'}),
            
            
            'api_url': forms.URLInput(attrs={'class': 'mask-api_url'}),
            'api_key': forms.TextInput(attrs={'class': 'mask-api_key'}),
            'api_secret': forms.TextInput(attrs={'class': 'mask-api_secret'}),
            'api_version': forms.TextInput(attrs={'class': 'mask-api_version'}),
            'emails_per_hour': forms.NumberInput(attrs={'class': 'mask-emails_per_hour'}),
            'emails_per_day': forms.NumberInput(attrs={'class': 'mask-emails_per_day'}),
            'max_recipients_per_email': forms.NumberInput(attrs={'class': 'mask-max_recipients_per_email'}),
            'test_email_address': forms.EmailInput(attrs={'class': 'mask-test_email_address'}),
            'connection_status': forms.Select(attrs={'class': 'mask-connection_status'}),
        }
        
        labels = {
            'provider_code': 'Código do Fornecedor',
            'description': 'Descrição',
            'is_active': 'Ativo',
            'api_url': 'URL da API',
            'api_key': 'Chave da API',
            'api_secret': 'Segredo da API',
            'api_version': 'Versão da API',
            'emails_per_hour': 'Limite de E-mails por Hora',
            'emails_per_day': 'Limite de E-mails por Dia',
            'max_recipients_per_email': 'Máximo de Destinatários por E-mail',
            'test_email_address': 'E-mail para Testes',
            'connection_status': 'Status de Conexão',
        }
        
        help_texts = {
            'provider_code': 'Digite o código do fornecedor',
            'description': 'Digite a descrição do fornecedor',
            'is_active': 'Fornecedor ativo',
            'api_url': 'Digite a URL da API (se aplicável)',
            'api_key': 'Digite a chave da API (se aplicável)',
            'api_secret': 'Digite o segredo da API (se aplicável)',
            'api_version': 'Digite a versão da API (se aplicável)',
            'emails_per_hour': 'Defina o limite de e-mails por hora (se aplicável)',
            'emails_per_day': 'Defina o limite de e-mails por dia (se aplicável)',
            'max_recipients_per_email': 'Defina o máximo de destinatários por e-mail (se aplicável)',
            'test_email_address': 'Digite um e-mail para testes de conexão',
            'connection_status': 'Selecione o status de conexão',
        }
        
        error_messages = {
            'provider_code': {
                'max_length': 'O código do fornecedor deve ter no máximo 50 caracteres.',
                'unique': 'O código do fornecedor deve ser único.',
            },
            'description': {
                'max_length': 'A descrição deve ter no máximo 100 caracteres.',
                'unique': 'A descrição deve ser única.',
            },
            'is_active': {
                'invalid': 'Selecione uma opção válida.',
            },
            'api_url': {
                'invalid': 'Digite uma URL válida.',
            },
            'api_key': {
                'max_length': 'A chave da API deve ter no.maxcdn 255 caracteres.',
            },
            'api_secret': {
                'max_length': 'O segredo da API deve ter no.maxcdn 255 caracteres.',
            },
            'api_version': {
                'max_length': 'A versão da API deve ter no.maxcdn 255 caracteres.',
            },
            'emails_per_hour': {
                'invalid': 'Digite um valor numérico.',
            },
            'emails_per_day': {
                'invalid': 'Digite um valor numérico.',
            },
            'max_recipients_per_email': {
                'invalid': 'Digite um valor numérico.',
            },
            'test_email_address': {
                'invalid': 'Digite um e-mail válido para testes.',
            },
            'connection_status': {
                'invalid': 'Selecione uma opção válida.',
            },
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provider_code'].widget.attrs['class'] = 'mask-provider_code'
        self.fields['description'].widget.attrs['class'] = 'mask-description'
        self.fields['is_active'].widget.attrs['class'] = 'mask-is_active'
        self.fields['api_url'].widget.attrs['class'] = 'mask-api_url'
        self.fields['api_key'].widget.attrs['class'] = 'mask-api_key'
        self.fields['api_secret'].widget.attrs['class'] = 'mask-api_secret'
        self.fields['api_version'].widget.attrs['class'] = 'mask-api_version'
        self.fields['emails_per_hour'].widget.attrs['class'] = 'mask-emails_per_hour'
        self.fields['emails_per_day'].widget.attrs['class'] = 'mask-emails_per_day'
        self.fields['max_recipients_per_email'].widget.attrs['class'] = 'mask-max_recipients_per_email'
        self.fields['test_email_address'].widget.attrs['class'] = 'mask-test_email_address'
        self.fields['connection_status'].widget.attrs['class'] = 'mask-connection_status'