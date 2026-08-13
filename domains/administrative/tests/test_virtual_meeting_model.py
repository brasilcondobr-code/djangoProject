import pytest
from django.db import IntegrityError, models
from django.utils import timezone
from domains.administrative.models import VirtualMeeting


def _base_data():
    now = timezone.now()
    return {
        'meeting_date_time_start': now + timezone.timedelta(days=1),
        'meeting_date_time_end': now + timezone.timedelta(days=2),
        'meeting_date_time_voting_begins': now + timezone.timedelta(days=1, hours=1),
        'meeting_date_time_voting_end': now + timezone.timedelta(days=2, hours=1),
        'meeting_date_time_send_mail': now + timezone.timedelta(days=1, minutes=30),
        'notice_meeting_date_time': now - timezone.timedelta(days=1),
    }


@pytest.mark.django_db
class TestVirtualMeetingModel:

    def test_create_virtual_meeting_minimal(self, _condo, _assembly_status):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo,
            title='Assembleia Geral Ordinária',
            president='Presidente',
            secretary='Secretário',
            meeting_status=_assembly_status,
            **_base_data(),
        )
        assert meeting.pk is not None
        assert meeting.title == 'Assembleia Geral Ordinária'
        assert meeting.meeting_status == _assembly_status
        assert meeting.created_at is not None
        assert meeting.updated_at is not None
        assert meeting.ban_those_in_default_from_voting is True

    def test_str_returns_title(self, _condo, _assembly_status):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo,
            title='Reunião de Condomínio',
            president='Presidente',
            secretary='Secretário',
            meeting_status=_assembly_status,
            **_base_data(),
        )
        assert str(meeting) == 'Reunião de Condomínio'

    def test_ordering_by_created_at_desc(self, _condo, _assembly_status):
        m1 = VirtualMeeting.objects.create(
            condominium=_condo, title='Primeira',
            president='P', secretary='S',
            meeting_status=_assembly_status, **_base_data(),
        )
        m2 = VirtualMeeting.objects.create(
            condominium=_condo, title='Segunda',
            president='P', secretary='S',
            meeting_status=_assembly_status, **_base_data(),
        )
        assert list(VirtualMeeting.objects.all()) == [m2, m1]

    def test_flags_booleans_created(self, _condo, _assembly_status):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo,
            title='Configurações',
            president='P', secretary='S',
            meeting_status=_assembly_status,
            ban_those_in_default_from_voting=True,
            allow_comments=True,
            **_base_data(),
        )
        assert meeting.ban_those_in_default_from_voting is True
        assert meeting.allow_comments is True
        assert meeting.hide_results_from_participants_during_voting is True
        assert meeting.show_replies_to_comments is False

    def test_notice_meeting_send_email_participants_default_true(self, _condo, _assembly_status):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo, title='Envio de e-mail',
            president='P', secretary='S',
            meeting_status=_assembly_status, **_base_data(),
        )
        assert meeting.notice_meeting_send_email_participants is True

    def test_condominium_relation(self, _condo, _assembly_status):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo, title='Relacionamento',
            president='P', secretary='S',
            meeting_status=_assembly_status, **_base_data(),
        )
        assert _condo.virtual_meetings.count() == 1
        assert _condo.virtual_meetings.first() == meeting

    def test_participating_vote_unit_default_true(self, _condo, _assembly_status):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo, title='Participantes',
            president='P', secretary='S',
            meeting_status=_assembly_status, **_base_data(),
        )
        assert meeting.participating_vote_unit is True

    def test_configuracoes_flags_default_true(self, _condo, _assembly_status):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo, title='Configurações',
            president='P', secretary='S',
            meeting_status=_assembly_status, **_base_data(),
        )
        assert meeting.ban_those_in_default_from_voting is True
        assert meeting.hide_results_from_participants_during_voting is True
        assert meeting.release_the_agenda_for_vote is True

    def test_participating_resident_relation(self, _condo, _assembly_status, _resident):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo, title='Participantes',
            president='P', secretary='S',
            meeting_status=_assembly_status,
            participating_vote_unit=True,
            **_base_data(),
        )
        meeting.participating_resident.add(_resident)
        assert meeting.participating_vote_unit is True
        assert list(meeting.participating_resident.all()) == [_resident]
        assert _resident.virtual_meetings_residents.filter(pk=meeting.pk).exists()

    def test_email_configuration_fields(self, _condo, _assembly_status, _smtp_config, _connection_pendente):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo, title='E-mail',
            president='P', secretary='S',
            meeting_status=_assembly_status,
            notice_meeting_title='Edital de Convocação Extraordinária',
            email_smtp_configuration=_smtp_config,
            connection_status=_connection_pendente,
            email_log='[2026-07-04 12:01:43] Enviado para Filas de Envio/Email',
            **_base_data(),
        )
        assert meeting.email_smtp_configuration == _smtp_config
        assert meeting.connection_status == _connection_pendente
        assert meeting.email_log == '[2026-07-04 12:01:43] Enviado para Filas de Envio/Email'
        assert meeting.notice_meeting_title == 'Edital de Convocação Extraordinária'

    def test_notice_meeting_title_max_length(self, _condo, _assembly_status):
        field = VirtualMeeting._meta.get_field('notice_meeting_title')
        assert isinstance(field, models.CharField)
        assert field.max_length == 250

    def test_meeting_date_time_send_mail_field_required(self, _condo, _assembly_status):
        field = VirtualMeeting._meta.get_field('meeting_date_time_send_mail')
        assert isinstance(field, models.DateTimeField)
        assert not field.null
        assert not field.blank

    def test_save_sets_connection_status_pendente_default(self, _condo, _assembly_status, _connection_pendente):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo, title='Status',
            president='P', secretary='S',
            meeting_status=_assembly_status,
            **_base_data(),
        )
        meeting.refresh_from_db()
        assert meeting.connection_status == _connection_pendente

    def test_save_preserves_explicit_connection_status(self, _condo, _assembly_status, _connection_enviado):
        meeting = VirtualMeeting.objects.create(
            condominium=_condo, title='Status',
            president='P', secretary='S',
            meeting_status=_assembly_status,
            connection_status=_connection_enviado,
            **_base_data(),
        )
        meeting.refresh_from_db()
        assert meeting.connection_status == _connection_enviado

    def test_end_must_be_after_start(self, _condo, _assembly_status):
        base = _base_data()
        base['meeting_date_time_end'] = base['meeting_date_time_start']
        with pytest.raises(IntegrityError):
            VirtualMeeting.objects.create(
                condominium=_condo, title='Datas inválidas',
                president='P', secretary='S',
                meeting_status=_assembly_status, **base,
            )

    def test_voting_end_must_be_after_begins(self, _condo, _assembly_status):
        base = _base_data()
        base['meeting_date_time_voting_end'] = base['meeting_date_time_voting_begins']
        with pytest.raises(IntegrityError):
            VirtualMeeting.objects.create(
                condominium=_condo, title='Datas inválidas',
                president='P', secretary='S',
                meeting_status=_assembly_status, **base,
            )

    def test_notice_must_be_before_start(self, _condo, _assembly_status):
        base = _base_data()
        base['notice_meeting_date_time'] = base['meeting_date_time_start']
        with pytest.raises(IntegrityError):
            VirtualMeeting.objects.create(
                condominium=_condo, title='Edital inválido',
                president='P', secretary='S',
                meeting_status=_assembly_status, **base,
            )