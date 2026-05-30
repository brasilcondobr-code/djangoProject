from django.db import models

class Notification(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "06. Notificação"
        verbose_name_plural = "06. Notificações"

    def __str__(self):
        return "06. Notificações"
