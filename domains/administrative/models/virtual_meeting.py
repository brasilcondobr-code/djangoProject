from django.conf import settings
from django.db import models


class VirtualMeeting(models.Model):
    class Meta:
        app_label = 'administrative'
        verbose_name = "11. Votação Virtual"
        verbose_name_plural = "11. Votações Virtuais"
        ordering = ['-created_at']
        db_table = 'administrative_virtualmeeting'
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    meeting_date_time_end__gt=models.F('meeting_date_time_start'),
                ),
                name='check_meeting_end_after_start',
            ),
            models.CheckConstraint(
                check=models.Q(
                    meeting_date_time_voting_end__gt=models.F(
                        'meeting_date_time_voting_begins',
                    ),
                ),
                name='check_voting_end_after_begins',
            ),
            models.CheckConstraint(
                check=models.Q(
                    notice_meeting_date_time__lt=models.F('meeting_date_time_start'),
                ),
                name='check_notice_before_start',
            ),
        ]
        indexes = [
            models.Index(fields=['condominium']),
            models.Index(fields=['meeting_status']),
            models.Index(fields=['meeting_date_time_start']),
            models.Index(fields=['meeting_date_time_end']),
            models.Index(fields=['notice_meeting_date_time']),
        ]

    # --- Aba: Principal ---
    condominium = models.ForeignKey(
        'condominium.Condominium',
        on_delete=models.CASCADE,
        related_name='virtual_meetings',
        verbose_name='Condomínio',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Título',
    )
    voting_type = models.ForeignKey(
        'parameters.VotingType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='virtual_meetings',
        verbose_name='Tipo de Votação',
    )
    location = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='Local',
    )
    meeting_date_time_start = models.DateTimeField(
        verbose_name='Início da assembleia',
    )
    meeting_date_time_end = models.DateTimeField(
        verbose_name='Término da assembleia',
    )
    meeting_date_time_voting_begins = models.DateTimeField(
        verbose_name='Início da votação',
    )
    meeting_date_time_voting_end = models.DateTimeField(
        verbose_name='Término da votação',
    )
    meeting_date_time_send_mail = models.DateTimeField(
        verbose_name='Data/Hora - Envio do E-mail',
    )
    president = models.CharField(
        max_length=250,
        verbose_name='Presidente',
    )
    secretary = models.CharField(
        max_length=250,
        verbose_name='Secretário',
    )
    video_conference_link = models.URLField(
        max_length=250,
        blank=True,
        verbose_name='Link da videoconferência',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição',
    )

    # --- Aba: Edital de Convocação ---
    notice_meeting_title = models.CharField(
        max_length=250,
        blank=True,
        default='',
        verbose_name='Título do Edital de Convocação',
    )
    notice_meeting_date_time = models.DateTimeField(
        verbose_name='Data da convocação',
    )
    notice_meeting_description = models.TextField(
        blank=True,
        verbose_name='Descrição do edital',
    )
    notice_meeting_send_email_participants = models.BooleanField(
        default=True,
        verbose_name='Enviar e-mail aos participantes',
    )

    # --- Aba: Configurações ---
    meeting_status = models.ForeignKey(
        'parameters.AssemblyStatus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='virtual_meetings',
        verbose_name='Status da assembleia',
    )
    ban_those_in_default_from_voting = models.BooleanField(
        default=True,
        verbose_name='Impedir inadimplentes de votar',
    )
    hide_results_from_participants_during_voting = models.BooleanField(
        default=True,
        verbose_name='Ocultar resultados durante a votação',
    )
    release_the_agenda_for_vote = models.BooleanField(
        default=True,
        verbose_name='Liberar a pauta para votação',
    )
    allow_comments = models.BooleanField(
        default=False,
        verbose_name='Permitir comentários',
    )
    show_comments = models.BooleanField(
        default=False,
        verbose_name='Exibir comentários',
    )
    allow_replies_to_comments = models.BooleanField(
        default=False,
        verbose_name='Permitir respostas aos comentários',
    )
    show_replies_to_comments = models.BooleanField(
        default=False,
        verbose_name='Exibir respostas aos comentários',
    )

    # --- Relacionamentos ---
    participating_vote_unit = models.BooleanField(
        default=True,
        verbose_name='Voto principal por unidade?',
    )
    participating_resident = models.ManyToManyField(
        'residents.Resident',
        related_name='virtual_meetings_residents',
        blank=True,
        verbose_name='Participantes',
    )
    participating_groups = models.ForeignKey(
        'parameters.ResidentType',
        on_delete=models.CASCADE,
        related_name='virtual_meetings',
        null=True,
        blank=True,
        verbose_name='Grupos participantes',
    )

    # --- Aba: Configurações (E-mail) ---
    email_smtp_configuration = models.ForeignKey(
        'email_service.SMTPConfiguration',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='virtual_meetings',
        verbose_name='Configuração SMTP',
    )
    connection_status = models.ForeignKey(
        'email_service.ConnectionStatus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='virtual_meetings',
        verbose_name='Email Status',
    )
    email_log = models.TextField(
        blank=True,
        default='',
        verbose_name='Email Logs',
        help_text='Histórico de registro dos envios de e-mails (somente leitura).',
    )

    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='created_virtual_meetings',
        verbose_name='Criado por',
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

    def save(self, *args, **kwargs):
        if self.connection_status_id is None:
            from domains.email_service.models import ConnectionStatus

            status_pendente = ConnectionStatus.objects.filter(
                status__iexact='Pendente',
            ).first()
            if status_pendente:
                self.connection_status = status_pendente
        super().save(*args, **kwargs)