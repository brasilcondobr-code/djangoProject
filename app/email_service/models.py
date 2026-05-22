from django.db import models

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
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "02. Status de Conexão"
        verbose_name_plural = "02. Status de Conexão"
        unique_together = ('status',)

    def __str__(self):
        return f"{self.status}"

class SMTP_Settings(models.Model):
    class Meta:
        verbose_name = "03. Configuração SMTP"
        verbose_name_plural = "03. Configurações SMTP"

    def __str__(self):
        return "03. Configurações SMTP"

class UsageProfiles(models.Model):
    class Meta:
        verbose_name = "04. Perfil de Uso"
        verbose_name_plural = "04. Perfis de Uso"

    def __str__(self):
        return "04. Perfis de Uso"

class ShippingQueue(models.Model):
    class Meta:
        verbose_name = "05. Fila de Envio"
        verbose_name_plural = "05. Filas de Envio"

    def __str__(self):
        return "05. Fila de Envio"

class EmailHistory(models.Model):
    class Meta:
        verbose_name = "06. Histórico de E-mail"
        verbose_name_plural = "06. Históricos de E-mails"

    def __str__(self):
        return "06. Histórico de E-mails"
