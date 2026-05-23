from django.db import models
from django.core.validators import MinValueValidator
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib

def get_encryption_key():
    key = settings.SECRET_KEY.encode()
    hashed_key = hashlib.sha256(key).digest()
    return base64.urlsafe_b64encode(hashed_key)

cipher_suite = Fernet(get_encryption_key())

def encrypt_value(value):
    if value:
        return cipher_suite.encrypt(value.encode()).decode()
    return value

def decrypt_value(value):
    if value:
        try:
            return cipher_suite.decrypt(value.encode()).decode()
        except Exception:
            return value
    return value

class TypesProvider(models.Model):
    provider = models.CharField(max_length=255, verbose_name="Provedor")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "01. Tipo de Provedor"
        verbose_name_plural = "01. Tipos de Provedores"
        unique_together = ('provider',)
    
    def __str__(self):
        return f"{self.provider}"

class ConnectionStatus(models.Model):
    status = models.CharField(max_length=255, verbose_name="Status de Conexão")
    description = models.CharField(max_length=255, verbose_name="Descrição", default='Sem descrição')
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "02. Status de Conexão"
        verbose_name_plural = "02. Status de Conexão"
        unique_together = ('status',)
    
    def __str__(self):
        return f"{self.status}"

class SMTPConfiguration(models.Model):
    # Aba: Main (Principal)
    description = models.CharField(
        verbose_name='Descrição',
        max_length=100,
        unique=True,
        null=False,
        blank=False
    )
    provider_code = models.CharField(
        verbose_name='Código do Provedor',
        max_length=50,
        unique=True,
        null=False,
        blank=False
    )
    provider_type = models.ForeignKey(
        TypesProvider,
        related_name='smtp_configuration',
        on_delete=models.CASCADE,
        verbose_name='Tipo de Provedor',
        null=False,
        blank=False
    )
    smtp_host = models.CharField(
        verbose_name='Host SMTP',
        max_length=255,
        null=False,
        blank=False
    )
    smtp_port = models.IntegerField(
        verbose_name='Porta SMTP',
        validators=[MinValueValidator(1)],
        null=False,
        blank=False
    )
    username = models.CharField(
        verbose_name='Nome de Usuário',
        max_length=255,
        blank=True,
        null=True
    )
    password = models.CharField(
        verbose_name='Senha',
        max_length=255,
        blank=True,
        null=True
    )
    use_tls = models.BooleanField(
        verbose_name='Utilizar TLS',
        default=True,
        choices=[(True, 'Sim'), (False, 'Não')]
    )
    use_ssl = models.BooleanField(
        verbose_name='Utilizar SSL',
        default=False,
        choices=[(True, 'Sim'), (False, 'Não')]
    )
    smtp_authentication = models.BooleanField(
        verbose_name='Requer autenticação SMTP',
        default=True,
        choices=[(True, 'Sim'), (False, 'Não')]
    )
    api_supported = models.BooleanField(
        verbose_name='Suporta API',
        default=False,
        choices=[(True, 'Sim'), (False, 'Não')]
    )
    is_default = models.BooleanField(
        verbose_name='Padrão',
        default=False
    )
    is_active = models.BooleanField(
        verbose_name='Ativo',
        default=True
    )
    created_at = models.DateTimeField(
        verbose_name='Criado em',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Atualizado em',
        auto_now=True
    )

    # Aba: API Configuration (Configuração API)
    api_url = models.URLField(
        verbose_name='URL API',
        max_length=500,
        null=True,
        blank=True
    )
    api_key = models.CharField(
        verbose_name='Chave API',
        max_length=255,
        blank=True,
        null=True
    )
    api_secret = models.CharField(
        verbose_name='Segredo API',
        max_length=255,
        blank=True,
        null=True
    )
    api_version = models.CharField(
        verbose_name='Versão API',
        max_length=50,
        null=True,
        blank=True
    )

    # Aba: Limits (Limites)
    emails_per_hour = models.IntegerField(
        verbose_name='Limite por hora',
        null=True,
        blank=True
    )
    emails_per_day = models.IntegerField(
        verbose_name='Limite por dia',
        null=True,
        blank=True
    )
    max_recipients_per_email = models.IntegerField(
        verbose_name='Máximo destinatários',
        null=True,
        blank=True
    )

    # Aba: Testing and Monitoring (Testes e Monitoramento)
    test_email_address = models.EmailField(
        verbose_name='E-mail para testes',
        max_length=255,
        null=True,
        blank=True
    )
    last_connection_tested_at = models.DateTimeField(
        verbose_name='Último teste',
        auto_now=False, # Changed from auto_now=True to allow manual updates or nulls
        null=True,
        blank=True
    )
    connection_status = models.ForeignKey(
        ConnectionStatus,
        related_name='smtp_configuration',
        on_delete=models.CASCADE,
        verbose_name='Status conexão',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = '04. Configuração SMTP'
        verbose_name_plural = '04. Configurações SMTP'
        ordering = ['description']
        unique_together = ('description', 'provider_code')

    def __str__(self):
        return f'{self.description} - {self.provider_code}'

    def save(self, *args, **kwargs):
        if self.is_default:
            SMTPConfiguration.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        
        # Encrypt password and api_secret before saving
        if self.password:
            # Avoid double encrypting
            if not self.password.startswith('enc:'):
                self.password = f"enc:{encrypt_value(self.password)}"
        
        if self.api_secret:
            if not self.api_secret.startswith('enc:'):
                self.api_secret = f"enc:{encrypt_value(self.api_secret)}"
                
        super().save(*args, **kwargs)

    @property
    def decrypted_password(self):
        if self.password and self.password.startswith('enc:'):
            return decrypt_value(self.password[4:])
        return self.password

    @property
    def decrypted_api_secret(self):
        if self.api_secret and self.api_secret.startswith('enc:'):
            return decrypt_value(self.api_secret[4:])
        return self.api_secret

class UsageProfiles(models.Model):
    class Meta:
        verbose_name = "05. Perfil de Uso"
        verbose_name_plural = "05. Perfis de Uso"
    def __str__(self):
        return "05. Perfis de Uso"

class ShippingQueue(models.Model):
    class Meta:
        verbose_name = "06. Fila de Envio"
        verbose_name_plural = "06. Filas de Envio"
    def __str__(self):
        return "06. Fila de Envio"

class EmailHistory(models.Model):
    class Meta:
        verbose_name = "07. Histórico de E-mail"
        verbose_name_plural = "07. Históricos de E-mails"
    def __str__(self):
        return "07. Histórico de E-mails"

