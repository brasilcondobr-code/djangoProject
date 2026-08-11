import pytest
from django.utils import timezone
from domains.administrative.models import VirtualMeeting, VirtualMeetingTopic, VirtualMeetingParticipant
from domains.administrative.services import (
    VirtualMeetingService,
    VirtualMeetingTopicService,
    VirtualMeetingParticipantService,
)
from domains.administrative.exceptions import (
    PendingStatusNotFound,
    VirtualMeetingValidationException,
    VirtualMeetingException,
    DuplicateTopicTitle,
)


def _data(_meeting, **overrides):
    data = {
        'condominium': _meeting.condominium,
        'title': 'Nova Assembleia',
        'president': 'Presidente A',
        'secretary': 'Secretário B',
        'meeting_date_time_start': _meeting.meeting_date_time_start,
        'meeting_date_time_end': _meeting.meeting_date_time_end,
        'meeting_date_time_voting_begins': _meeting.meeting_date_time_voting_begins,
        'meeting_date_time_voting_end': _meeting.meeting_date_time_voting_end,
        'notice_meeting_date_time': _meeting.notice_meeting_date_time,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestVirtualMeetingService:

    def test_create_virtual_meeting(self, _meeting, _assembly_status):
        created = VirtualMeetingService.create_virtual_meeting(_data(_meeting))
        assert created.condominium_id == _meeting.condominium_id
        assert created.meeting_status == _assembly_status
        assert created.title == 'Nova Assembleia'

    def test_create_assigns_pending_status_when_missing(self, _condo):
        now = timezone.now()
        status = __import__('domains.parameters.models', fromlist=['AssemblyStatus']).AssemblyStatus.objects.create(
            description='Pendente 2', is_pending=True,
        )
        created = VirtualMeetingService.create_virtual_meeting({
            'condominium': _condo,
            'title': 'Sem status',
            'president': 'P',
            'secretary': 'S',
            'meeting_date_time_start': now + timezone.timedelta(days=1),
            'meeting_date_time_end': now + timezone.timedelta(days=2),
            'meeting_date_time_voting_begins': now + timezone.timedelta(days=1, hours=1),
            'meeting_date_time_voting_end': now + timezone.timedelta(days=1, hours=2),
            'notice_meeting_date_time': now - timezone.timedelta(days=1),
        })
        assert created.meeting_status == status

    def test_create_raises_without_pending_status(self, _condo):
        now = timezone.now()
        import pytest as _pytest
        with _pytest.raises(PendingStatusNotFound):
            VirtualMeetingService.create_virtual_meeting({
                'condominium': _condo,
                'title': 'Sem status',
                'president': 'P',
                'secretary': 'S',
                'meeting_date_time_start': now + timezone.timedelta(days=1),
                'meeting_date_time_end': now + timezone.timedelta(days=2),
                'meeting_date_time_voting_begins': now + timezone.timedelta(days=1, hours=1),
                'meeting_date_time_voting_end': now + timezone.timedelta(days=1, hours=2),
                'notice_meeting_date_time': now - timezone.timedelta(days=1),
            })

    def test_create_requires_title(self, _meeting):
        with pytest.raises(VirtualMeetingValidationException):
            VirtualMeetingService.create_virtual_meeting(_data(_meeting, title=''))

    def test_update_virtual_meeting(self, _meeting):
        updated = VirtualMeetingService.update_virtual_meeting(_meeting, {'title': 'Título Atualizado'})
        assert updated.title == 'Título Atualizado'

    def test_update_ignores_meeting_status(self, _meeting):
        updated = VirtualMeetingService.update_virtual_meeting(
            _meeting, {'meeting_status': None, 'title': 'Novo'},
        )
        assert updated.meeting_status is not None
        assert updated.title == 'Novo'

    def test_update_invalid_dates(self, _meeting):
        with pytest.raises(VirtualMeetingValidationException):
            VirtualMeetingService.update_virtual_meeting(
                _meeting,
                {
                    'meeting_date_time_start': _meeting.meeting_date_time_end,
                    'meeting_date_time_end': _meeting.meeting_date_time_start,
                },
            )

    def test_delete_virtual_meeting(self, _meeting):
        pk = _meeting.pk
        VirtualMeetingService.delete_virtual_meeting(_meeting)
        assert not VirtualMeeting.objects.filter(pk=pk).exists()

    def test_get_pending_status(self, _assembly_status):
        assert VirtualMeetingService.get_pending_status() == _assembly_status

    def test_is_notice_future(self, _meeting):
        assert VirtualMeetingService.is_notice_future(_meeting) is False


@pytest.mark.django_db
class TestVirtualMeetingTopicService:

    def test_create_topic(self, _meeting):
        topic = VirtualMeetingTopicService.create_topic(_meeting, {'title': 'Pauta 1'})
        assert topic.title == 'Pauta 1'
        assert topic.virtual_meeting == _meeting

    def test_create_topic_duplicate(self, _meeting):
        VirtualMeetingTopicService.create_topic(_meeting, {'title': 'Pauta 1'})
        with pytest.raises(DuplicateTopicTitle):
            VirtualMeetingTopicService.create_topic(_meeting, {'title': 'pauta 1'})

    def test_topic_title_exists(self, _meeting):
        assert VirtualMeetingTopicService.topic_title_exists(_meeting, 'Pauta 1') is False
        VirtualMeetingTopicService.create_topic(_meeting, {'title': 'Pauta 1'})
        assert VirtualMeetingTopicService.topic_title_exists(_meeting, 'Pauta 1') is True

    def test_topic_title_exists_unsaved_meeting_returns_false(self, _condo, _assembly_status):
        from django.utils import timezone
        now = timezone.now()
        meeting = VirtualMeeting(
            condominium=_condo,
            title='Assembleia nova',
            president='João',
            secretary='Maria',
            meeting_status=_assembly_status,
            meeting_date_time_start=now + timezone.timedelta(days=1),
            meeting_date_time_end=now + timezone.timedelta(days=2),
            meeting_date_time_voting_begins=now + timezone.timedelta(days=1, hours=1),
            meeting_date_time_voting_end=now + timezone.timedelta(days=1, hours=2),
            notice_meeting_date_time=now - timezone.timedelta(days=1),
        )
        assert VirtualMeetingTopicService.topic_title_exists(meeting, 'Pauta 1') is False

    def test_update_topic(self, _meeting):
        topic = VirtualMeetingTopicService.create_topic(_meeting, {'title': 'Pauta 1'})
        VirtualMeetingTopicService.update_topic(topic, {'title': 'Pauta Renomeada'})
        topic.refresh_from_db()
        assert topic.title == 'Pauta Renomeada'


@pytest.mark.django_db
class TestVirtualMeetingParticipantService:

    def test_add_participant(self, _meeting, _resident_type, _resident):
        participant = VirtualMeetingParticipantService.add_participant(
            _meeting, _resident_type, _resident,
        )
        assert participant.resident == _resident
        assert participant.resident_type == _resident_type

    def test_add_participant_type_mismatch(self, _meeting, _resident_type, _resident):
        from domains.parameters.models import ResidentType
        outro = ResidentType.objects.create(description='Inquilino')
        _resident.type_of_resident = _resident_type
        _resident.save()
        with pytest.raises(VirtualMeetingException):
            VirtualMeetingParticipantService.add_participant(_meeting, outro, _resident)

    def test_get_participants(self, _meeting, _resident_type, _resident):
        VirtualMeetingParticipantService.add_participant(_meeting, _resident_type, _resident)
        participants = VirtualMeetingParticipantService.get_participants(_meeting)
        assert participants.count() == 1

    def test_remove_participant(self, _meeting, _resident_type, _resident):
        participant = VirtualMeetingParticipantService.add_participant(_meeting, _resident_type, _resident)
        VirtualMeetingParticipantService.remove_participant(participant)
        assert not VirtualMeetingParticipant.objects.filter(pk=participant.pk).exists()