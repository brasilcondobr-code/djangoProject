from django.db import models

class Agreement(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "01. Acordo"
        verbose_name_plural = "01. Acordos"

    def __str__(self):
        return "01. Acordo"

class PaymentSlip(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "02. Boleto"
        verbose_name_plural = "02. Boletos"

    def __str__(self):
        return "02. Boleto"

class Cash(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "03. Caixa"
        verbose_name_plural = "03. Caixa"

    def __str__(self):
        return "03. Caixa"

class Collection(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "04. Cobrança"
        verbose_name_plural = "04. Cobranças"

    def __str__(self):
        return "04. Cobrança"

class Shopping(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "05. Compra"
        verbose_name_plural = "05. Compras"

    def __str__(self):
        return "05. Compra"

class Loan(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "06. Empréstimo"
        verbose_name_plural = "06. Empréstimos"

    def __str__(self):
        return "06. Empréstimo"

class NewRelease(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "07. Lançamento"
        verbose_name_plural = "07. Lançamentos"

    def __str__(self):
        return "07. Lançamento"

class Payment(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "08. Pagamento"
        verbose_name_plural = "08. Pagamentos"

    def __str__(self):
        return "08. Pagamento"

class Apportionment(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "09. Rateio"
        verbose_name_plural = "09. Rateios"

    def __str__(self):
        return "09. Rateio"

class Receipt(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "10. Recebimento"
        verbose_name_plural = "10. Recebimentos"

    def __str__(self):
        return "10. Recebimento"

class BankTransfer(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "11. Remessa Bancária"
        verbose_name_plural = "11. Remessas Bancárias"

    def __str__(self):
        return "11. Remessa Bancária"
