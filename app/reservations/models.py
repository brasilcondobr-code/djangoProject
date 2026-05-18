from django.db import models

class Rentals(models.Model):

    class Meta:
        verbose_name = "01. Locação"
        verbose_name_plural = "01. Locações"

    def __str__(self):
        return "01. Locações"

class MaintenanceReservations(models.Model):

    class Meta:
        verbose_name = "02. Manutenção"
        verbose_name_plural = "02. Manutenções"

    def __str__(self):
        return "02. Manutenções"

class MoveReservations(models.Model):

    class Meta:
        verbose_name = "03. Mudança"
        verbose_name_plural = "03. Mudanças"

    def __str__(self):
        return "03. Mudanças"

class Reforms(models.Model):

    class Meta:
        verbose_name = "04. Reforma"
        verbose_name_plural = "04. Reformas"

    def __str__(self):
        return "04. Reformas"