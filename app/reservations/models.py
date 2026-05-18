from django.db import models

class Rentals(models.Model):

    class Meta:
        verbose_name = "1. Locação"
        verbose_name_plural = "1. Locações"

    def __str__(self):
        return "1. Locações"

class MaintenanceReservations(models.Model):

    class Meta:
        verbose_name = "2. Manutenção"
        verbose_name_plural = "2. Manutenções"

    def __str__(self):
        return "2. Manutenções"

class MoveReservations(models.Model):

    class Meta:
        verbose_name = "3. Mudança"
        verbose_name_plural = "3. Mudanças"

    def __str__(self):
        return "3. Mudanças"

class Reforms(models.Model):

    class Meta:
        verbose_name = "4. Reforma"
        verbose_name_plural = "4. Reformas"

    def __str__(self):
        return "4. Reformas"