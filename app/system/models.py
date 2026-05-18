from django.db import models

class TechnicalSupportTicket(models.Model):
    class Meta:
        verbose_name = "01. Chamado Técnico"
        verbose_name_plural = "01. Chamados Técnicos"

    def __str__(self):
        return "01. Chamados Técnicos"

class EmailConfiguration(models.Model):
    class Meta:
        verbose_name = "02. Configuração de E-mail"
        verbose_name_plural = "02. Configurações de E-mail"

    def __str__(self):
        return "02. Configurações de E-mail"

class SMSConfiguration(models.Model):
    class Meta:
        verbose_name = "03. Configuração SMS"
        verbose_name_plural = "03. Configurações SMS"

    def __str__(self):
        return "03. Configurações SMS"

class WhatsAppSettings(models.Model):
    class Meta:
        verbose_name = "04. Configuração WhatsApp"
        verbose_name_plural = "04. Configurações WhatsApp"

    def __str__(self):
        return "04. Configurações WhatsApp"

class SystemLog(models.Model):
    class Meta:
        verbose_name = "05. Log do Sistema"
        verbose_name_plural = "05. Logs do Sistema"

    def __str__(self):
        return "05. Logs do Sistema"

class AutomatedRoutine(models.Model):
    class Meta:
        verbose_name = "06. Rotina Automática"
        verbose_name_plural = "06. Rotinas Automáticas"

    def __str__(self):
        return "06. Rotinas Automáticas"

class Training(models.Model):
    class Meta:
        verbose_name = "07. Treinamento"
        verbose_name_plural = "07. Treinamentos"

    def __str__(self):
        return "07. Treinamentos"

class IntegrationToken(models.Model):
    class Meta:
        verbose_name = "08. Token de Integração"
        verbose_name_plural = "08. Tokens de Integração"

    def __str__(self):
        return "08. Tokens de Integração"

class ConnectedUser(models.Model):
    class Meta:
        verbose_name = "09. Usuário Conectado"
        verbose_name_plural = "09. Usuários Conectados"

    def __str__(self):
        return "09. Usuários Conectados"
