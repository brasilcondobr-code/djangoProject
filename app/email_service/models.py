from django.db import models

class SMTP_Settings(models.Model):
    class Meta:
        verbose_name = "01. Configuração SMTP"
        verbose_name_plural = "01. Configurações SMTP"

    def __str__(self):
        return "01. Configurações SMTP"

class UsageProfiles(models.Model):
    class Meta:
        verbose_name = "02. Perfil de Uso"
        verbose_name_plural = "02. Perfis de Uso"

    def __str__(self):
        return "02. Perfis de Uso"

class ShippingQueue(models.Model):
    class Meta:
        verbose_name = "03. Fila de Envio"
        verbose_name_plural = "03. Filas de Envio"

    def __str__(self):
        return "03. Fila de Envio"

class EmailHistory(models.Model):
    class Meta:
        verbose_name = "04. Histórico de E-mail"
        verbose_name_plural = "04. Históricos de E-mails"

    def __str__(self):
        return "04. Histórico de E-mails"
