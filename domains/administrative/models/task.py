from django.db import models

class Task(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "10. Tarefa"
        verbose_name_plural = "10. Tarefas"

    def __str__(self):
        return "10. Tarefas"
