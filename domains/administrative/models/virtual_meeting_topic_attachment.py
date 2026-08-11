from django.db import models

from domains.administrative.models.virtual_meeting_topic import VirtualMeetingTopic

from domains.administrative.validators import validate_topic_attachment_extension, validate_file_size_10mb


class VirtualMeetingTopicAttachment(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "Anexo da Pauta"
        verbose_name_plural = "Anexos das Pautas"
        ordering = ['-created_at']
        db_table = 'administrative_virtualmeetingtopicattachment'
        indexes = [
            models.Index(fields=['topic']),
        ]

    topic = models.ForeignKey(
        VirtualMeetingTopic,
        related_name='attachments',
        on_delete=models.CASCADE,
        verbose_name='Pauta',
    )
    file = models.FileField(
        upload_to='administrative/virtual_meetings/topics/',
        verbose_name='Arquivo',
        validators=[validate_topic_attachment_extension, validate_file_size_10mb],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )

    def __str__(self):
        return self.file.name