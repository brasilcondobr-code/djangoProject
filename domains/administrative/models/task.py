from django.db import models

class Task(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "09. Tarefa"
        verbose_name_plural = "09. Tarefas"

    def __str__(self):
        return "09. Tarefas"
