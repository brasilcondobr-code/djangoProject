from django.db import models

class TechnicalSupportTicket(models.Model):
    class Meta:
        verbose_name = "01. Chamado Técnico"
        verbose_name_plural = "01. Chamados Técnicos"

    def __str__(self):
        return "01. Chamados Técnicos"

class SystemLog(models.Model):
    class Meta:
        verbose_name = "02. Log do Sistema"
        verbose_name_plural = "02. Logs do Sistema"

    def __str__(self):
        return "02. Logs do Sistema"

class AutomatedRoutine(models.Model):
    class Meta:
        verbose_name = "03. Rotina Automática"
        verbose_name_plural = "03. Rotinas Automáticas"

    def __str__(self):
        return "03. Rotinas Automáticas"

class Training(models.Model):
    class Meta:
        verbose_name = "04. Treinamento"
        verbose_name_plural = "04. Treinamentos"

    def __str__(self):
        return "04. Treinamentos"

class IntegrationToken(models.Model):
    class Meta:
        verbose_name = "05. Token de Integração"
        verbose_name_plural = "05. Tokens de Integração"

    def __str__(self):
        return "05. Tokens de Integração"

class ConnectedUser(models.Model):
    class Meta:
        verbose_name = "06. Usuário Conectado"
        verbose_name_plural = "06. Usuários Conectados"

    def __str__(self):
        return "06. Usuários Conectados"
