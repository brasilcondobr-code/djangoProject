from django.db import models

class Shift(models.Model):

    class Meta:
        verbose_name = "1. Plantão"
        verbose_name_plural = "1. Plantões"

    def __str__(self):
        return "1. Plantões"

class ServiceTransition(models.Model):

    class Meta:
        verbose_name = "2. Passagem de Serviço"
        verbose_name_plural = "2. Passagens de Serviços"

    def __str__(self):
        return "2. Passagens de Serviços"

class UsefulPhoneNumber(models.Model):

    class Meta:
        verbose_name = "3. Telefone Útil"
        verbose_name_plural = "3. Telefones Úteis"

    def __str__(self):
        return "3. Telefones Úteis"

class Order(models.Model):

    class Meta:
        verbose_name = "4. Encomenda"
        verbose_name_plural = "4. Encomendas"

    def __str__(self):
        return "4. Encomendas"

class VisitorsRegister(models.Model):

    class Meta:
        verbose_name = "5. Reg. Visitante"
        verbose_name_plural = "5. Reg. Visitantes"

    def __str__(self):
        return "5. Reg. Visitantes"

class Correspondence(models.Model):

    class Meta:
        verbose_name = "6. Correspondência"
        verbose_name_plural = "6. Correspondências"

    def __str__(self):
        return "6. Correspondências"

class Occurrence(models.Model):

    class Meta:
        verbose_name = "7. Ocorrência"
        verbose_name_plural = "7. Ocorrências"

    def __str__(self):
        return "7. Ocorrências"

class Bag(models.Model):

    class Meta:
        verbose_name = "8. Malote"
        verbose_name_plural = "8. Malotes"

    def __str__(self):
        return "8. Malotes"

class ElectronicTimeClock(models.Model):

    class Meta:
        verbose_name = "9. Ponto Eletrônico"
        verbose_name_plural = "9. Pontos Eletrônicos"

    def __str__(self):
        return "9. Ponto Eletrônico"