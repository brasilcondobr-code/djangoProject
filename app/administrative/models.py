from django.db import models

class Bank(models.Model):
    class Meta:
        verbose_name = "1. Banco"
        verbose_name_plural = "1. Bancos"

    def __str__(self):
        return "1. Bancos"

class Circular(models.Model):
    class Meta:
        verbose_name = "2. Circular"
        verbose_name_plural = "2. Circulares"

    def __str__(self):
        return "2. Circulares"

class Contract(models.Model):
    class Meta:
        verbose_name = "3. Contrato"
        verbose_name_plural = "3. Contratos"

    def __str__(self):
        return "3. Contratos"

class Infraction(models.Model):
    class Meta:
        verbose_name = "4. Infração"
        verbose_name_plural = "4. Infrações"

    def __str__(self):
        return "4. Infrações"

class Meter(models.Model):
    class Meta:
        verbose_name = "5. Medidor"
        verbose_name_plural = "5. Medidores"

    def __str__(self):
        return "5. Medidores"

class Notification(models.Model):
    class Meta:
        verbose_name = "6. Notificação"
        verbose_name_plural = "6. Notificações"

    def __str__(self):
        return "6. Notificações"

class Patrimony(models.Model):
    class Meta:
        verbose_name = "7. Patrimônio"
        verbose_name_plural = "7. Patrimônios"

    def __str__(self):
        return "7. Patrimônios"

class BudgetForecast(models.Model):
    class Meta:
        verbose_name = "8. Previsão Orçamentária"
        verbose_name_plural = "8. Previsões Orçamentárias"

    def __str__(self):
        return "8. Previsões Orçamentárias"

class ChartOfAccount(models.Model):
    class Meta:
        verbose_name = "9. Plano de Conta"
        verbose_name_plural = "9. Plano de Contas"

    def __str__(self):
        return "9. Plano de Contas"

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
