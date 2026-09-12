import logging

from django.db import IntegrityError, transaction

from domains.administrative.exceptions import VirtualMeetingException
from domains.administrative.models.virtual_meeting_participant import VirtualMeetingParticipant
from domains.residents.models import Resident

logger = logging.getLogger(__name__)


class VirtualMeetingParticipantService:

    @staticmethod
    @transaction.atomic
    def add_participant(virtual_meeting, resident_type, resident):
        if resident_type and resident_type.pk and resident.type_of_resident_id != resident_type.pk:
            raise VirtualMeetingException(
                'O morador selecionado não pertence ao tipo de residente escolhido.'
            )

        try:
            return VirtualMeetingParticipant.objects.create(
                virtual_meeting=virtual_meeting,
                resident_type=resident_type,
                resident=resident,
            )
        except IntegrityError as exc:
            raise VirtualMeetingException(
                'Este morador já é participante desta assembleia.'
            ) from exc

    @staticmethod
    def get_participants(virtual_meeting):
        return VirtualMeetingParticipant.objects.filter(
            virtual_meeting=virtual_meeting,
        ).select_related('resident', 'resident_type')

    @staticmethod
    @transaction.atomic
    def remove_participant(participant):
        participant.delete()
        logger.info(
            'virtual_meeting_participant_removed',
            extra={
                'virtual_meeting_id': participant.virtual_meeting_id,
                'participant_id': participant.pk,
                'operation': 'delete',
            },
        )

    @staticmethod
    def get_residents_by_groups(group_ids, condominium=None):
        if not group_ids:
            return Resident.objects.none()

        queryset = (
            Resident.objects.filter(
                type_of_resident_id__in=group_ids,
                is_active=True,
            )
            .select_related('unit__condominium', 'type_of_resident')
            .distinct()
            .order_by('name')
        )

        if condominium:
            queryset = queryset.filter(unit__condominium=condominium)

        return queryset

    @staticmethod
    def get_invalid_participant_ids(participant_ids, group_ids, condominium=None):
        if not participant_ids:
            return set()

        valid_ids = set(
            VirtualMeetingParticipantService.get_residents_by_groups(
                group_ids, condominium=condominium,
            )
            .filter(pk__in=participant_ids)
            .values_list('pk', flat=True)
        )

        return set(participant_ids) - valid_ids