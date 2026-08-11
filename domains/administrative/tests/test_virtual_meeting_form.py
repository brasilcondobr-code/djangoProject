import pytest
from django.utils import timezone
from domains.administrative.forms import (
    VirtualMeetingForm,
    VirtualMeetingTopicForm,
    VirtualMeetingParticipantForm,
)


def _form_data(meeting, **overrides):
    data = {
        'condominium': meeting.condominium_id,
        'title': 'Assembleia Geral',
        'president': 'João',
        'secretary': 'Maria',
        'meeting_date_time_start': meeting.meeting_date_time_start,
        'meeting_date_time_end': meeting.meeting_date_time_end,
        'meeting_date_time_voting_begins': meeting.meeting_date_time_voting_begins,
        'meeting_date_time_voting_end': meeting.meeting_date_time_voting_end,
        'notice_meeting_date_time': meeting.notice_meeting_date_time,
        'notice_meeting_send_email_participants': False,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestVirtualMeetingForm:

    def test_valid_form(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting))
        assert form.is_valid(), form.errors

    def test_empty_title(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting, title='   '))
        assert not form.is_valid()
        assert 'Informe o título da assembleia.' in form.errors['title']

    def test_end_before_start(self, _meeting):
        data = _form_data(
            _meeting,
            meeting_date_time_start=_meeting.meeting_date_time_end,
            meeting_date_time_end=_meeting.meeting_date_time_start,
        )
        form = VirtualMeetingForm(data=data)
        assert not form.is_valid()
        assert 'O término da assembleia deve ser maior que o início.' in form.errors['meeting_date_time_end']

    def test_notice_not_before_start(self, _meeting):
        data = _form_data(
            _meeting,
            notice_meeting_date_time=_meeting.meeting_date_time_start,
        )
        form = VirtualMeetingForm(data=data)
        assert not form.is_valid()
        assert 'A data de convocação deve ser anterior ao início da assembleia.' in form.errors['notice_meeting_date_time']

    def test_strips_whitespace(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting, title='  Assembleia Importante  '))
        assert form.is_valid(), form.errors
        assert form.cleaned_data['title'] == 'Assembleia Importante'

    def test_participantes_fields(self, _meeting, _resident_type, _resident):
        _resident.type_of_resident = _resident_type
        _resident.save()
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_vote_unit=True,
            participating_groups=_resident_type.pk,
            participating_resident=[_resident.pk],
        ))
        assert form.is_valid(), form.errors
        assert form.cleaned_data['participating_vote_unit'] is True
        assert list(form.cleaned_data['participating_resident']) == [_resident]

    def test_voting_begins_before_start(self, _meeting):
        new_start = _meeting.meeting_date_time_voting_begins + timezone.timedelta(minutes=30)
        data = _form_data(
            _meeting,
            meeting_date_time_start=new_start,
            meeting_date_time_end=new_start + timezone.timedelta(days=1),
        )
        form = VirtualMeetingForm(data=data)
        assert not form.is_valid()
        assert 'O início da votação não pode ser anterior ao início da assembleia.' in form.errors['meeting_date_time_voting_begins']

    def test_voting_end_after_end(self, _meeting):
        data = _form_data(
            _meeting,
            meeting_date_time_voting_end=_meeting.meeting_date_time_end + timezone.timedelta(days=1),
        )
        form = VirtualMeetingForm(data=data)
        assert not form.is_valid()
        assert 'O término da votação não pode ser posterior ao término da assembleia.' in form.errors['meeting_date_time_voting_end']


@pytest.mark.django_db
class TestVirtualMeetingTopicForm:

    def test_valid_topic_form(self, _meeting):
        form = VirtualMeetingTopicForm(data={
            'virtual_meeting': _meeting.pk,
            'title': 'Aprovação do balanço',
        })
        assert form.is_valid(), form.errors
        topic = form.save()
        assert topic.title == 'Aprovação do balanço'
        assert topic.virtual_meeting == _meeting

    def test_duplicate_topics(self, _meeting):
        VirtualMeetingTopicForm(data={
            'virtual_meeting': _meeting.pk,
            'title': 'Aprovação do balanço',
        }).save()

        form2 = VirtualMeetingTopicForm(data={
            'virtual_meeting': _meeting.pk,
            'title': 'Aprovação do BALANÇO',
        })
        assert not form2.is_valid()
        assert 'Já existe uma pauta com este título nesta assembleia.' in form2.errors['title'][0]

    def test_blank_title(self, _meeting):
        form = VirtualMeetingTopicForm(data={
            'virtual_meeting': _meeting.pk,
            'title': '   ',
        })
        assert not form.is_valid()
        assert 'Informe o título da pauta.' in form.errors['title']


@pytest.mark.django_db
class TestVirtualMeetingParticipantForm:

    def test_resident_not_in_type(self, _meeting, _resident_type, _resident):
        from domains.parameters.models import ResidentType
        outro_tipo = ResidentType.objects.create(description='Inquilino')
        _resident.type_of_resident = _resident_type
        _resident.save()

        form = VirtualMeetingParticipantForm(data={
            'virtual_meeting': _meeting.pk,
            'resident_type': outro_tipo.pk,
            'resident': _resident.pk,
        })
        assert not form.is_valid()
        assert 'não pertence ao tipo' in form.errors['resident'][0]

    def test_valid_participant(self, _meeting, _resident_type, _resident):
        _resident.type_of_resident = _resident_type
        _resident.save()
        form = VirtualMeetingParticipantForm(data={
            'virtual_meeting': _meeting.pk,
            'resident_type': _resident_type.pk,
            'resident': _resident.pk,
        })
        assert form.is_valid(), form.errors