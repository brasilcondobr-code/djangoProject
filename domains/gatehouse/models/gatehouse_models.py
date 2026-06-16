from django.db import models

class Shift(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "01. Plantão"
        verbose_name_plural = "01. Plantões"

    def __str__(self):
        return "01. Plantão"

class ServiceTransition(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "02. Passagem de Serviço"
        verbose_name_plural = "02. Passagens de Serviços"

    def __str__(self):
        return "02. Passagem de Serviço"

class UsefulPhoneNumber(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "03. Telefone Útil"
        verbose_name_plural = "03. Telefones Úteis"

    def __str__(self):
        return "03. Telefone Útil"

class Order(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "04. Encomenda"
        verbose_name_plural = "04. Encomendas"

    def __str__(self):
        return "04. Encomenda"

class VisitorsRegister(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "05. Reg. Visitante"
        verbose_name_plural = "05. Reg. Visitantes"

    def __str__(self):
        return "05. Reg. Visitante"

class Correspondence(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "06. Correspondência"
        verbose_name_plural = "06. Correspondências"

    def __str__(self):
        return "06. Correspondência"

class Occurrence(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "07. Ocorrência"
        verbose_name_plural = "07. Ocorrências"

    def __str__(self):
        return "07. Ocorrência"

class Bag(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "08. Malote"
        verbose_name_plural = "08. Malotes"

    def __str__(self):
        return "08. Malote"

class ElectronicTimeClock(models.Model):
    class Meta:
        app_label = 'gatehouse'
        verbose_name = "09. Ponto Eletrônico"
        verbose_name_plural = "09. Pontos Eletrônicos"

    def __str__(self):
        return "09. Ponto Eletrônico"
