import logging

from django.db import transaction
from django.utils import timezone

from domains.administrative.exceptions import (
    PendingStatusNotFound,
    VirtualMeetingValidationException,
)
from domains.administrative.models.virtual_meeting import VirtualMeeting
from domains.parameters.models import AssemblyStatus

logger = logging.getLogger(__name__)


class VirtualMeetingService:

    @staticmethod
    def normalize_text(value):
        if value is None:
            return ''
        return value.strip()

    @staticmethod
    def get_pending_status():
        status = AssemblyStatus.objects.filter(is_pending=True).first()
        if not status:
            raise PendingStatusNotFound(
                'Não existe um status de assembleia pendente cadastrado.'
            )
        return status

    @staticmethod
    def validate_meeting_dates(data):
        start = data.get('meeting_date_time_start')
        end = data.get('meeting_date_time_end')
        voting_begins = data.get('meeting_date_time_voting_begins')
        voting_end = data.get('meeting_date_time_voting_end')
        notice = data.get('notice_meeting_date_time')

        if start and end and end <= start:
            raise VirtualMeetingValidationException(
                'O término da assembleia deve ser maior que o início.'
            )
        if voting_begins and voting_end and voting_end <= voting_begins:
            raise VirtualMeetingValidationException(
                'O término da votação deve ser maior que o início da votação.'
            )
        if start and voting_begins and voting_begins < start:
            raise VirtualMeetingValidationException(
                'O início da votação não pode ser anterior ao início da assembleia.'
            )
        if end and voting_end and voting_end > end:
            raise VirtualMeetingValidationException(
                'O término da votação não pode ser posterior ao término da assembleia.'
            )
        if notice and start and notice >= start:
            raise VirtualMeetingValidationException(
                'A data de convocação deve ser anterior ao início da assembleia.'
            )

        VirtualMeetingService.validate_date(data)

    @staticmethod
    def validate_date(data):
        send_mail = data.get('meeting_date_time_send_mail')
        voting_begins = data.get('meeting_date_time_voting_begins')
        if not send_mail or not voting_begins:
            return
        if send_mail >= voting_begins:
            raise VirtualMeetingValidationException(
                'A data/hora de envio do e-mail deve ser anterior ao início da votação.',
            )

    @staticmethod
    @transaction.atomic
    def create_virtual_meeting(data):
        data = dict(data)
        for field in ('title', 'president', 'secretary', 'location'):
            if field in data:
                data[field] = VirtualMeetingService.normalize_text(data.get(field))

        if not data.get('title'):
            raise VirtualMeetingValidationException('Informe o título da assembleia.')
        if not data.get('president'):
            raise VirtualMeetingValidationException('Informe o presidente da assembleia.')
        if not data.get('secretary'):
            raise VirtualMeetingValidationException('Informe o secretário da assembleia.')

        VirtualMeetingService.validate_meeting_dates(data)

        if not data.get('meeting_status'):
            data['meeting_status'] = VirtualMeetingService.get_pending_status()

        virtual_meeting = VirtualMeeting.objects.create(**data)
        logger.info(
            'virtual_meeting_created',
            extra={
                'virtual_meeting_id': virtual_meeting.pk,
                'condominium_id': virtual_meeting.condominium_id,
                'operation': 'create',
            },
        )
        return virtual_meeting

    @staticmethod
    @transaction.atomic
    def update_virtual_meeting(virtual_meeting, data):
        data = dict(data)
        for field in ('title', 'president', 'secretary', 'location'):
            if field in data:
                data[field] = VirtualMeetingService.normalize_text(data.get(field))

        if 'meeting_status' in data:
            data.pop('meeting_status')

        VirtualMeetingService.validate_meeting_dates(data)

        for attr, value in data.items():
            setattr(virtual_meeting, attr, value)
        virtual_meeting.save()
        logger.info(
            'virtual_meeting_updated',
            extra={
                'virtual_meeting_id': virtual_meeting.pk,
                'condominium_id': virtual_meeting.condominium_id,
                'operation': 'update',
            },
        )
        return virtual_meeting

    @staticmethod
    @transaction.atomic
    def delete_virtual_meeting(virtual_meeting):
        virtual_meeting.delete()
        logger.info(
            'virtual_meeting_deleted',
            extra={
                'virtual_meeting_id': virtual_meeting.pk,
                'operation': 'delete',
            },
        )

    @staticmethod
    def is_notice_future(virtual_meeting):
        if not virtual_meeting.notice_meeting_date_time:
            return False
        return virtual_meeting.notice_meeting_date_time > timezone.now()