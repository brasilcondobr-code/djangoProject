import logging

from django.db import transaction
from django.utils import timezone

from domains.administrative.exceptions import VirtualMeetingValidationException
from domains.administrative.services.circular_email_queue_service import AdministrativeEmailQueueService
from domains.administrative.services.virtual_meeting_participant_service import VirtualMeetingParticipantService

logger = logging.getLogger(__name__)

EMAIL_MODULE_ORIGIN = 'virtual_meeting'


class VirtualMeetingEmailService:

    @staticmethod
    def build_subject(virtual_meeting):
        return f'Convocação: {virtual_meeting.title}'

    @staticmethod
    def build_message(virtual_meeting):
        description = virtual_meeting.notice_meeting_description or ''
        return (
            f'Informamos que foi publicado o edital de convocação da '
            f'assembleia "{virtual_meeting.title}".\n\n'
            f'Data: {virtual_meeting.meeting_date_time_start:%d/%m/%Y às %H:%M}.\n'
            f'{description}'
        )

    @staticmethod
    def _collect_residents(virtual_meeting):
        participants = VirtualMeetingParticipantService.get_participants(virtual_meeting)
        residents = [participant.resident for participant in participants if participant.resident.email]
        return residents

    @staticmethod
    def validate_meeting_for_queue(virtual_meeting):
        if not VirtualMeetingParticipantService.get_participants(virtual_meeting).exists():
            raise VirtualMeetingValidationException(
                'Não é possível enfileirar o envio: a assembleia não possui participantes.'
            )

        if not virtual_meeting.notice_meeting_send_email_participants:
            raise VirtualMeetingValidationException(
                'O envio de e-mail aos participantes não está habilitado para esta assembleia.'
            )

    @staticmethod
    @transaction.atomic
    def queue_notice_email(virtual_meeting):
        VirtualMeetingEmailService.validate_meeting_for_queue(virtual_meeting)

        residents = VirtualMeetingEmailService._collect_residents(virtual_meeting)
        if not residents:
            raise VirtualMeetingValidationException(
                'Nenhum participante possui e-mail cadastrado para o envio.'
            )

        results = AdministrativeEmailQueueService.queue_emails(
            entity=virtual_meeting,
            residents=residents,
            module_origin=EMAIL_MODULE_ORIGIN,
            subject=VirtualMeetingEmailService.build_subject(virtual_meeting),
            message=VirtualMeetingEmailService.build_message(virtual_meeting),
            smtp_config_field='',
        )

        logger.info(
            'virtual_meeting_email_queued',
            extra={
                'virtual_meeting_id': virtual_meeting.pk,
                'queued': results.get('queued'),
                'already_queued': results.get('already_queued'),
                'no_email': results.get('no_email'),
                'errors': results.get('errors'),
                'operation': 'queue_email',
            },
        )
        return results

    @staticmethod
    def schedule_notice_email(virtual_meeting):
        results = VirtualMeetingEmailService.queue_notice_email(virtual_meeting)

        from domains.administrative.tasks.virtual_meeting_email_tasks import (
            process_virtual_meeting_email_task,
        )

        eta = None
        if VirtualMeetingEmailService.is_notice_future(virtual_meeting):
            eta = virtual_meeting.notice_meeting_date_time

        task = process_virtual_meeting_email_task.apply_async(
            kwargs={'virtual_meeting_id': virtual_meeting.pk},
            eta=eta,
        )
        logger.info(
            'virtual_meeting_email_scheduled',
            extra={
                'virtual_meeting_id': virtual_meeting.pk,
                'celery_task_id': task.id,
                'eta': eta.isoformat() if eta else None,
                'operation': 'schedule_task',
            },
        )
        return task

    @staticmethod
    def is_notice_future(virtual_meeting):
        if not virtual_meeting.notice_meeting_date_time:
            return False
        return virtual_meeting.notice_meeting_date_time > timezone.now()