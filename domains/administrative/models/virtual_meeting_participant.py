from django.db import models

from domains.administrative.models.virtual_meeting import VirtualMeeting


class VirtualMeetingParticipant(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        ordering = ['resident__name']
        db_table = 'administrative_virtualmeetingparticipant'
        constraints = [
            models.UniqueConstraint(
                fields=['virtual_meeting', 'resident'],
                name='unique_resident_per_virtual_meeting',
            ),
        ]
        indexes = [
            models.Index(fields=['virtual_meeting']),
            models.Index(fields=['resident']),
        ]

    virtual_meeting = models.ForeignKey(
        VirtualMeeting,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Assembleia',
    )
    resident_type = models.ForeignKey(
        'parameters.ResidentType',
        on_delete=models.PROTECT,
        related_name='virtual_meeting_participants',
        verbose_name='Tipo de Residente',
    )
    resident = models.ForeignKey(
        'residents.Resident',
        on_delete=models.CASCADE,
        related_name='virtual_meeting_participants',
        verbose_name='Morador',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )

    def __str__(self):
        return f'{self.resident} ({self.resident_type})'