from django.db import models

from domains.administrative.models.virtual_meeting import VirtualMeeting


class VirtualMeetingTopic(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "Pauta"
        verbose_name_plural = "Pautas"
        ordering = ['title']
        db_table = 'administrative_virtualmeetingtopic'
        constraints = [
            models.UniqueConstraint(
                fields=('virtual_meeting', 'title'),
                name='unique_topic_title_per_virtual_meeting',
            ),
        ]
        indexes = [
            models.Index(fields=['virtual_meeting']),
        ]

    virtual_meeting = models.ForeignKey(
        VirtualMeeting,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name='Assembleia',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Título',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição',
    )
    topic_options = models.ManyToManyField(
        'parameters.TopicOption',
        related_name='virtual_meeting_topics',
        blank=True,
        verbose_name='Opções de votação',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    def __str__(self):
        return self.title