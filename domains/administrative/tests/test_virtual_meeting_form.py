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
        'description': '<p>Descrição da assembleia</p>',
        'president': 'João',
        'secretary': 'Maria',
        'meeting_date_time_start': meeting.meeting_date_time_start,
        'meeting_date_time_end': meeting.meeting_date_time_end,
        'meeting_date_time_voting_begins': meeting.meeting_date_time_voting_begins,
        'meeting_date_time_voting_end': meeting.meeting_date_time_voting_end,
        'meeting_date_time_send_mail': (
            meeting.meeting_date_time_voting_begins - timezone.timedelta(days=1)
        ),
        'notice_meeting_title': 'Edital de Convocação',
        'notice_meeting_date_time': meeting.notice_meeting_date_time,
        'notice_meeting_description': '<p>Descrição do edital</p>',
        'notice_meeting_send_email_participants': False,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestVirtualMeetingForm:

    def test_valid_form(self, _meeting, _resident_type, _resident, _smtp_config, _connection_pendente):
        _resident.type_of_resident = _resident_type
        _resident.save()
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups=_resident_type.pk,
            participating_resident=[_resident.pk],
            email_smtp_configuration=_smtp_config.pk,
            connection_status=_connection_pendente.pk,
        ))
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

    def test_strips_whitespace(self, _meeting, _resident_type, _resident, _smtp_config, _connection_pendente):
        _resident.type_of_resident = _resident_type
        _resident.save()
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            title='  Assembleia Importante  ',
            participating_groups=_resident_type.pk,
            participating_resident=[_resident.pk],
            email_smtp_configuration=_smtp_config.pk,
            connection_status=_connection_pendente.pk,
        ))
        assert form.is_valid(), form.errors
        assert form.cleaned_data['title'] == 'Assembleia Importante'

    def test_participantes_fields(self, _meeting, _resident_type, _resident, _smtp_config, _connection_pendente):
        _resident.type_of_resident = _resident_type
        _resident.save()
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_vote_unit=True,
            participating_groups=_resident_type.pk,
            participating_resident=[_resident.pk],
            email_smtp_configuration=_smtp_config.pk,
            connection_status=_connection_pendente.pk,
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

    def test_email_configuration_fields(self, _meeting, _resident_type, _resident, _smtp_config, _connection_pendente):
        _resident.type_of_resident = _resident_type
        _resident.save()
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups=_resident_type.pk,
            participating_resident=[_resident.pk],
            email_smtp_configuration=_smtp_config.pk,
            connection_status=_connection_pendente.pk,
        ))
        assert form.is_valid(), form.errors
        assert form.cleaned_data['email_smtp_configuration'] == _smtp_config
        assert form.cleaned_data['connection_status'] == _connection_pendente
        assert 'email_log' in form.fields
        assert form.fields['email_log'].label == 'Email Logs'

    def test_connection_status_initial_pendente_on_new(self, _connection_pendente):
        form = VirtualMeetingForm()
        assert form.fields['connection_status'].initial == _connection_pendente

    def test_meeting_date_time_send_mail_required(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting, meeting_date_time_send_mail=''))
        assert not form.is_valid()
        assert 'Informe a data de envio do e-mail.' in form.errors['meeting_date_time_send_mail']

    def test_meeting_date_time_send_mail_after_voting_begins(self, _meeting):
        data = _form_data(
            _meeting,
            meeting_date_time_send_mail=(
                _meeting.meeting_date_time_voting_begins.date()
                + timezone.timedelta(days=1)
            ),
        )
        form = VirtualMeetingForm(data=data)
        assert not form.is_valid()
        assert 'A data/hora de envio do e-mail deve ser anterior ao início da votação.' in form.errors['meeting_date_time_send_mail']

    def test_notice_meeting_title_required(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting, notice_meeting_title='   '))
        assert not form.is_valid()
        assert 'Informe o título do edital de convocação.' in form.errors['notice_meeting_title']

    def test_description_required(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting, description=''))
        assert not form.is_valid()
        assert 'Informe a descrição da assembleia.' in form.errors['description']

    def test_description_empty_html_required(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting, description='<p>&nbsp;</p>'))
        assert not form.is_valid()
        assert 'Informe a descrição da assembleia.' in form.errors['description']

    def test_notice_meeting_description_required(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting, notice_meeting_description=''))
        assert not form.is_valid()
        assert 'Informe a descrição do edital.' in form.errors['notice_meeting_description']

    def test_participating_groups_required(self, _meeting):
        form = VirtualMeetingForm(data=_form_data(_meeting))
        assert not form.is_valid()
        assert 'Selecione ao menos um grupo de participantes.' in form.errors['participating_groups']

    def test_participating_resident_required(self, _meeting, _resident_type):
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups=_resident_type.pk,
        ))
        assert not form.is_valid()
        assert 'Selecione ao menos um participante.' in form.errors['participating_resident']

    def test_email_smtp_configuration_required(self, _meeting, _resident_type, _resident, _connection_pendente):
        _resident.type_of_resident = _resident_type
        _resident.save()
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups=_resident_type.pk,
            participating_resident=[_resident.pk],
            connection_status=_connection_pendente.pk,
        ))
        assert not form.is_valid()
        assert 'Selecione a configuração SMTP.' in form.errors['email_smtp_configuration']

    def test_connection_status_required(self, _meeting, _resident_type, _resident, _smtp_config):
        _resident.type_of_resident = _resident_type
        _resident.save()
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups=_resident_type.pk,
            participating_resident=[_resident.pk],
            email_smtp_configuration=_smtp_config.pk,
        ))
        assert not form.is_valid()
        assert 'Selecione o status do e-mail.' in form.errors['connection_status']


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
            'title': 'Aprovacao do balanco',
        }).save()

        form2 = VirtualMeetingTopicForm(data={
            'virtual_meeting': _meeting.pk,
            'title': 'Aprovacao do BALANCO',
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