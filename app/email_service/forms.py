from django import forms
from django.core.exceptions import ValidationError
from .models import ConnectionStatus, TypesProvider, SMTPConfiguration, UsageProfiles, ShippingQueue
import uuid

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
            'password': forms.TextInput(attrs={'class': 'mask-password'}),
            'use_tls': forms.Select(),
            'use_ssl': forms.Select(),
            'smtp_authentication': forms.Select(),
            'api_supported': forms.Select(),
            'is_default': forms.CheckboxInput(),
            'is_active': forms.CheckboxInput(),
            'api_url': forms.URLInput(attrs={'class': 'mask-api_url', 'placeholder': 'https://api.provider.com'}),
            'api_key': forms.TextInput(attrs={'class': 'mask-api_key'}),
            'api_secret': forms.TextInput(attrs={'class': 'mask-api_secret'}),
            'api_version': forms.TextInput(attrs={'class': 'mask-api_version'}),
            'emails_per_hour': forms.NumberInput(attrs={'class': 'mask-number'}),
            'emails_per_day': forms.NumberInput(attrs={'class': 'mask-number'}),
            'max_recipients_per_email': forms.NumberInput(attrs={'class': 'mask-number'}),
            'test_email_address': forms.EmailInput(attrs={'class': 'mask-email'}),
            'last_connection_tested_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'connection_status': forms.Select(),
            'last_error_message': forms.Textarea(attrs={'class': 'mask-last_error_message', 'rows': 3}),
            'last_test_duration': forms.NumberInput(attrs={'class': 'mask-number', 'placeholder': 'Tempo em segundos'}),
        }
        
        labels = {
            'description': 'Descrição',
            'provider_code': 'Código do Provedor',
            'provider_type': 'Tipo de Provedor',
            'smtp_host': 'Host SMTP',
            'smtp_port': 'Porta SMTP',
            'username': 'Usuário',
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
            'last_error_message': 'Mensagem de erro',
            'last_test_duration': 'Tempo de teste',
        }
        
        help_texts = {
            'description': 'Descrição curta para identificação do provedor.',
            'provider_code': 'Código único do provedor para integração.',
            'provider_type': 'Tipo de provedor.',
            'smtp_host': 'Endereço do servidor SMTP.',
            'smtp_port': 'Porta de conexão do servidor SMTP.',
            'username': 'Usuário para autenticação SMTP.',
            'password': 'Senha para autenticação SMTP.',
            'use_tls': 'Indica se a conexão deve usar TLS.',
            'use_ssl': 'Indica se a conexão deve usar SSL.',
            'smtp_authentication': 'Indica se a autenticação SMTP é necessária.',
            'api_supported': 'Indica se o provedor suporta integração via API.',
            'is_default': 'Indica se esta configuração é a padrão.',
            'is_active': 'Indica se esta configuração está ativa.',
            'api_url': 'URL base para chamadas de API.',
            'api_key': 'Chave de acesso para autenticação API.',
            'api_secret': 'Segredo para autenticação API.',
            'api_version': 'Versão da API utilizada.',
            'emails_per_hour': 'Número máximo de e-mails que podem ser enviados por hora.',
            'emails_per_day': 'Número máximo de e-mails que podem ser enviados por dia.',
            'max_recipients_per_email': 'Número máximo de destinatários permitidos por e-mail.',
            'test_email_address': 'Endereço de e-mail para envio de testes.',
            'last_connection_tested_at': 'Data e hora do último teste de conexão.',
            'connection_status': 'Status atual da conexão.',
            'last_error_message': 'Última mensagem de erro registrada durante testes de conexão.',
            'last_test_duration': 'Duração do último teste de conexão em segundos.',
        }
        
        error_messages = {}

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
                self.add_error('username', 'O usuário é obrigatório quando a autenticação SMTP está ativa.')
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_classes = {
            'description': 'mask-description',
            'provider_code': 'mask-provider_code',
            'smtp_host': 'mask-smtp_host',
            'smtp_port': 'mask-smtp_port',
            'username': 'mask-username',
            'password': 'mask-password',
            'use_tls': 'mask-use_tls',
            'use_ssl': 'mask-use_ssl',
            'smtp_authentication': 'mask-smtp_authentication',
            'api_supported': 'mask-api_supported',
            'is_default': 'mask-is_default',
            'is_active': 'mask-is_active',
            'api_url': 'mask-api_url',
            'api_key': 'mask-api_key',
            'api_secret': 'mask-api_secret',
            'api_version': 'mask-api_version',
            'emails_per_hour': 'mask-number',
            'emails_per_day': 'mask-number',
            'max_recipients_per_email': 'mask-number',
            'test_email_address': 'mask-email',
            'last_connection_tested_at': 'mask-last_connection_tested_at',
            'connection_status': 'mask-connection_status',
            'last_error_message': 'mask-last_error_message',
            'last_test_duration': 'mask-last_test_duration',
        }
        for field_name, class_name in field_classes.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = class_name
        

class UsageProfilesForm(forms.ModelForm):
    class Meta:
        model = UsageProfiles
        fields = '__all__'
        widgets = {
            'purpose': forms.TextInput(attrs={'class': 'mask-purpose', 'placeholder': 'Ex: Marketing, Transacional'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is_active'}),
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'updated_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        
        labels = {
            'purpose': 'Propósito',
            'is_active': 'Ativo',
            'created_at': 'Data de Criação',
            'updated_at': 'Data de Atualização',
        }
        
        help_texts = {
            'purpose': 'Informe a finalidade de utilização deste perfil.',
            'is_active': 'Status de conexão ativo',
            'created_at': 'Data de Criação',
            'updated_at': 'Data de Atualização',
        }
        
        error_messages = {
            'purpose': {
                'max_length': 'O propósitos deve ter no máximo 255 caracteres.',
            },
            'is_active': {
                'invalid': 'Selecione uma opção válida.',
            },
        }
    
    def clean_purpose(self):
        purpose = self.cleaned_data.get('purpose')
        if not purpose:
            raise forms.ValidationError('O propósitos é obrigatório.')
        if len(purpose) > 255:
            raise forms.ValidationError('O propósitos deve ter no máximo 255 caracteres.')
        return purpose.strip()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['purpose'].widget.attrs['class'] = 'mask-purpose'
        self.fields['is_active'].widget.attrs['class'] = 'mask-is_active'


class ShippingQueueForm(forms.ModelForm):
    class Meta:
        model = ShippingQueue
        fields = '__all__'
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'mask-subject'}),
            'to_email': forms.EmailInput(attrs={'class': 'mask-email'}),
            'cc': forms.Textarea(attrs={'rows': 2, 'class': 'mask-text'}),
            'bcc': forms.Textarea(attrs={'rows': 2, 'class': 'mask-text'}),
            'reply_to': forms.EmailInput(attrs={'class': 'mask-email'}),
            'message': forms.Textarea(attrs={'rows': 5, 'class': 'mask-text'}),
            'html_message': forms.Textarea(attrs={'rows': 5, 'class': 'mask-text'}),
            'attachments': forms.FileInput(),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'next_retry_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'processing_started_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sent_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

        labels = {
            'subject': 'Assunto',
            'to_email': 'Destinatário',
            'cc': 'CC',
            'bcc': 'BCC',
            'reply_to': 'Responder para',
            'message': 'Mensagem',
            'html_message': 'Mensagem HTML',
            'attachments': 'Anexos',
            'scheduled_at': 'Agendado para',
            'next_retry_at': 'Próxima tentativa',
            'processing_started_at': 'Processamento iniciado em',
            'sent_at': 'Enviado em',
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Validação de duplicidade básica
        to_email = cleaned_data.get('to_email')
        subject = cleaned_data.get('subject')
        module_origin = cleaned_data.get('module_origin')
        reference_id = cleaned_data.get('reference_id')
        is_active = cleaned_data.get('is_active')

        if to_email and subject and module_origin and reference_id and is_active:
            from email_service.models import ShippingQueue
            duplicate = ShippingQueue.objects.filter(
                to_email=to_email,
                subject=subject,
                module_origin=module_origin,
                reference_id=reference_id,
                is_active=True
            ).exists()
            
            if duplicate:
                raise ValidationError("Já existe um envio pendente para este destinatário, assunto, origem e referência.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes de máscara para os campos de texto se necessário
        if 'subject' in self.fields:
            self.fields['subject'].widget.attrs['class'] = 'mask-subject'
        if 'to_email' in self.fields:
            self.fields['to_email'].widget.attrs['class'] = 'mask-email'
        if 'message' in self.fields:
            self.fields['message'].widget.attrs['class'] = 'mask-text'
        if 'html_message' in self.fields:
            self.fields['html_message'].widget.attrs['class'] = 'mask-text'
