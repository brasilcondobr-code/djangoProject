from django.db import models

class Shift(models.Model):

    class Meta:
        verbose_name = "Plantão"
        verbose_name_plural = "Plantões"

    def __str__(self):
        return "Plantões"

class ServiceTransition(models.Model):

    class Meta:
        verbose_name = "Passagem de Serviço"
        verbose_name_plural = "Passagens de Serviços"

    def __str__(self):
        return "Passagens de Serviços"

class UsefulPhoneNumber(models.Model):

    class Meta:
        verbose_name = "Telefone Útil"
        verbose_name_plural = "Telefones Úteis"

    def __str__(self):
        return "Telefones Úteis"

class Order(models.Model):

    class Meta:
        verbose_name = "Encomenda"
        verbose_name_plural = "Encomendas"

    def __str__(self):
        return "Encomendas"

class VisitorsRegister(models.Model):

    class Meta:
        verbose_name = "Visitante"
        verbose_name_plural = "Visitantes"

    def __str__(self):
        return "Visitantes"

class Correspondence(models.Model):

    class Meta:
        verbose_name = "Correspondência"
        verbose_name_plural = "Correspondências"

    def __str__(self):
        return "Correspondências"

class Occurrence(models.Model):

    class Meta:
        verbose_name = "Ocorrência"
        verbose_name_plural = "Ocorrências"

    def __str__(self):
        return "Ocorrências"

class Bag(models.Model):

    class Meta:
        verbose_name = "Malote"
        verbose_name_plural = "Malotes"

    def __str__(self):
        return "Malotes"

class Circular(models.Model):

    class Meta:
        verbose_name = "Circular"
        verbose_name_plural = "Circulares"

    def __str__(self):
        return "Circulares"

class Task(models.Model):

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    def __str__(self):
        return "Tarefas"
