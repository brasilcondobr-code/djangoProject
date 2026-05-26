from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

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
        max_length=500,
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
        max_length=500,
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
        auto_now=False,
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
    last_error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Último erro'
    )
    last_test_duration = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Tempo teste (segundos)'
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
        super().save(*args, **kwargs)

class UsageProfiles(models.Model):
    purpose = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name='Propósito',
        help_text='Informe a finalidade de utilização deste perfil.'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )

    class Meta:
        verbose_name = '05. Perfil de Uso'
        verbose_name_plural = '05. Perfis de Uso'
        ordering = ['purpose']
        constraints = [
            models.UniqueConstraint(
                fields=['purpose'],
                name='unique_usage_profile_purpose'
            )
        ]

    def __str__(self):
        return self.purpose

    def clean(self):
        super().clean()
        if self.purpose:
            self.purpose = self.purpose.strip()
        
        if not self.purpose or not self.purpose.strip():
            raise ValidationError("O campo Propósito é obrigatório.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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



