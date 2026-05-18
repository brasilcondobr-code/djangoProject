from django.db import models

class Bank(models.Model):
    class Meta:
        verbose_name = "01. Banco"
        verbose_name_plural = "01. Bancos"

    def __str__(self):
        return "01. Bancos"

class Circular(models.Model):
    class Meta:
        verbose_name = "02. Circular"
        verbose_name_plural = "02. Circulares"

    def __str__(self):
        return "02. Circulares"

class Contract(models.Model):
    class Meta:
        verbose_name = "03. Contrato"
        verbose_name_plural = "03. Contratos"

    def __str__(self):
        return "03. Contratos"

class Infraction(models.Model):
    class Meta:
        verbose_name = "04. Infração"
        verbose_name_plural = "04. Infrações"

    def __str__(self):
        return "04. Infrações"

class Meter(models.Model):
    class Meta:
        verbose_name = "05. Medidor"
        verbose_name_plural = "05. Medidores"

    def __str__(self):
        return "05. Medidores"

class Notification(models.Model):
    class Meta:
        verbose_name = "06. Notificação"
        verbose_name_plural = "06. Notificações"

    def __str__(self):
        return "06. Notificações"

class Patrimony(models.Model):
    class Meta:
        verbose_name = "07. Patrimônio"
        verbose_name_plural = "07. Patrimônios"

    def __str__(self):
        return "07. Patrimônios"

class BudgetForecast(models.Model):
    class Meta:
        verbose_name = "08. Previsão Orçamentária"
        verbose_name_plural = "08. Previsões Orçamentárias"

    def __str__(self):
        return "08. Previsões Orçamentárias"

class ChartOfAccount(models.Model):
    class Meta:
        verbose_name = "09. Plano de Conta"
        verbose_name_plural = "09. Plano de Contas"

    def __str__(self):
        return "09. Plano de Contas"

class Project(models.Model):
    class Meta:
        verbose_name = "10. Projeto"
        verbose_name_plural = "10. Projetos"

    def __str__(self):
        return "10. Projetos"

class Task(models.Model):
    class Meta:
        verbose_name = "11. Tarefa"
        verbose_name_plural = "11. Tarefas"

    def __str__(self):
        return "11. Tarefas"

class VirtualAssembly(models.Model):
    class Meta:
        verbose_name = "12. Assembleia Virtual"
        verbose_name_plural = "12. Assembleias Virtuais"

    def __str__(self):
        return "12. Assembleias Virtuais"
