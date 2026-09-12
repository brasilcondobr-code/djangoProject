import pytest

from domains.administrative.exceptions import VirtualMeetingValidationException
from domains.administrative.services.virtual_meeting_email_service import (
    VirtualMeetingEmailService,
)
from domains.data_management.models import ScheduledTaskModule, ScheduledTaskRecipient
from domains.email_service.models import ShippingQueue


def _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente):
    _meeting.description = '<p>Descrição da assembleia</p>'
    _meeting.notice_meeting_title = 'Edital de Convocação'
    _meeting.notice_meeting_description = '<p>Descrição do edital</p>'
    _meeting.notice_meeting_send_email_participants = True
    _meeting.email_smtp_configuration = _smtp_config
    _meeting.connection_status = _connection_pendente
    _meeting.save()
    _meeting.participating_resident.add(_resident)
    return _meeting


@pytest.mark.django_db
class TestVirtualMeetingEmailService:

    def test_build_subject_notice(self, _meeting):
        _meeting.notice_meeting_title = 'Edital de Convocação Extraordinária'
        subject = VirtualMeetingEmailService.build_subject(
            _meeting,
            ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE,
        )
        assert subject == 'Edital de Convocação: Edital de Convocação Extraordinária'

    def test_build_subject_voting(self, _meeting):
        subject = VirtualMeetingEmailService.build_subject(
            _meeting,
            ScheduledTaskModule.TaskType.VIRTUAL_MEETING_VOTING,
        )
        assert subject == f'Convocação para Votação: {_meeting.title}'

    def test_build_message_uses_plain_content(self, _meeting):
        _meeting.notice_meeting_description = '<p>Compareça <strong>obrigatoriamente</strong>.</p>'
        message = VirtualMeetingEmailService.build_message(
            _meeting,
            ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE,
        )
        assert 'Compareça' in message
        assert '<p>' not in message
        assert _meeting.title in message

    def test_validate_without_participants(self, _meeting):
        assert 'Participantes selecionados' in VirtualMeetingEmailService.get_validation_errors(
            _meeting,
        )
        with pytest.raises(VirtualMeetingValidationException):
            VirtualMeetingEmailService.schedule_emails(_meeting)

    def test_schedule_emails_creates_both_tasks(
        self, _meeting, _resident, _smtp_config, _connection_pendente, _connection_enviado,
    ):
        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        results = VirtualMeetingEmailService.schedule_emails(_meeting)
        assert results['skipped'] is False
        assert len(results['schedules']) == 2
        types = {s['task_type'] for s in results['schedules']}
        assert types == {'notice', 'voting'}

        tasks = ScheduledTaskModule.objects.filter(
            virtual_meeting=_meeting,
        ).order_by('task_type')
        assert tasks.count() == 2
        notice = tasks.get(task_type=ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE)
        voting = tasks.get(task_type=ScheduledTaskModule.TaskType.VIRTUAL_MEETING_VOTING)
        assert notice.scheduled_at == _meeting.notice_meeting_date_time
        assert voting.scheduled_at == _meeting.meeting_date_time_send_mail
        assert notice.recipients.count() == 1
        assert voting.recipients.count() == 1
        _meeting.refresh_from_db()
        assert 'Agendamento criado: Edital de Convocação' in _meeting.email_log
        assert 'Agendamento criado: Convocação para Votação' in _meeting.email_log
        assert _meeting.connection_status.status.lower() == 'enviado'

    def test_schedule_emails_skips_when_flag_false(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        _meeting.notice_meeting_send_email_participants = False
        _meeting.save()
        results = VirtualMeetingEmailService.schedule_emails(_meeting)
        assert results['skipped'] is True
        assert ScheduledTaskModule.objects.filter(
            virtual_meeting=_meeting,
        ).count() == 0
        _meeting.refresh_from_db()
        assert 'Envio de e-mail desabilitado' in _meeting.email_log

    def test_schedule_emails_ignores_residents_without_email(
        self, _meeting, _resident, _smtp_config, _connection_pendente, _condo_unit,
    ):
        from domains.residents.models.resident import Resident

        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        Resident.objects.create(
            unit=_condo_unit,
            type_of_resident=_resident.type_of_resident,
            name='Maria Sem Email',
            email='',
            phone='(11) 98888-0000',
            cpf='111.222.333-44',
            rg='11.222.333-4',
            sex='F',
            date_of_birth='1985-01-01',
        )
        _meeting.participating_resident.add(
            Resident.objects.get(name='Maria Sem Email'),
        )
        result = VirtualMeetingEmailService.schedule_emails(_meeting)
        assert result['no_email'] == 1
        for task in ScheduledTaskModule.objects.filter(virtual_meeting=_meeting):
            assert task.recipients.count() == 1

    def test_schedule_is_restarted_when_triggered_again(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        VirtualMeetingEmailService.schedule_emails(_meeting)
        task = ScheduledTaskModule.objects.get(
            virtual_meeting=_meeting,
            task_type=ScheduledTaskModule.TaskType.VIRTUAL_MEETING_VOTING,
        )
        VirtualMeetingEmailService.schedule_emails(_meeting)
        task.refresh_from_db()
        assert task.status == ScheduledTaskModule.Status.PENDING
        assert task.recipients.count() == 1

    def test_get_validation_errors_aggregates_pending(self, _meeting):
        errors = VirtualMeetingEmailService.get_validation_errors(_meeting)
        assert 'Condomínio' not in errors
        assert 'Título' not in errors
        for expected in (
            'Descrição/conteúdo da assembleia',
            'Título do edital de convocação',
            'Descrição do edital',
            'Participantes selecionados',
            'Configuração SMTP',
            'Email Status (Pendente)',
        ):
            assert expected in errors

    def test_validation_allows_email_flag_false(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        _meeting.notice_meeting_send_email_participants = False
        _meeting.save()
        assert VirtualMeetingEmailService.get_validation_errors(_meeting) == []

    def test_process_recipient_sends_and_logs(
        self, _meeting, _resident, _smtp_config, _connection_pendente, _connection_enviado,
    ):
        from unittest.mock import patch

        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        VirtualMeetingEmailService.schedule_emails(_meeting)
        task = ScheduledTaskModule.objects.get(
            virtual_meeting=_meeting,
            task_type=ScheduledTaskModule.TaskType.VIRTUAL_MEETING_VOTING,
        )
        recipient = task.recipients.first()

        with patch(
            'domains.email_service.services.queue_processor_service.QueueProcessorService.process_single_item',
            return_value={'success': True, 'message': 'ok'},
        ):
            result = VirtualMeetingEmailService.process_recipient(recipient.pk)

        assert result['success'] is True
        recipient.refresh_from_db()
        assert recipient.status == ScheduledTaskRecipient.Status.SENT
        assert recipient.sent_at is not None
        task.refresh_from_db()
        assert task.status == ScheduledTaskModule.Status.SENT
        _meeting.refresh_from_db()
        assert 'Enviado para Filas de Envio/Email: Convocação para Votação' in _meeting.email_log
        assert ShippingQueue.objects.filter(
            module_origin='virtual_meeting_voting',
            reference_id=_meeting.pk,
            to_email=_resident.email,
        ).exists()

    def test_process_recipient_failure_marks_failed(
        self, _meeting, _resident, _smtp_config, _connection_pendente, _connection_enviado,
    ):
        from unittest.mock import patch

        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        VirtualMeetingEmailService.schedule_emails(_meeting)
        task = ScheduledTaskModule.objects.get(
            virtual_meeting=_meeting,
            task_type=ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE,
        )
        recipient = task.recipients.first()

        with patch(
            'domains.email_service.services.queue_processor_service.QueueProcessorService.process_single_item',
            return_value={'success': False, 'message': 'SMTP unavailable'},
        ):
            result = VirtualMeetingEmailService.process_recipient(recipient.pk)

        assert result['success'] is False
        recipient.refresh_from_db()
        assert recipient.status == ScheduledTaskRecipient.Status.FAILED
        assert 'SMTP unavailable' in recipient.last_error
        task.refresh_from_db()
        assert task.status == ScheduledTaskModule.Status.FAILED

    def test_schedule_emails_raises_when_validation_fails(self, _meeting):
        with pytest.raises(VirtualMeetingValidationException):
            VirtualMeetingEmailService.schedule_emails(_meeting)

    def test_dispatch_recipients_queues_per_recipient_task(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        from unittest.mock import patch

        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        VirtualMeetingEmailService.schedule_emails(_meeting)
        task = ScheduledTaskModule.objects.get(
            virtual_meeting=_meeting,
            task_type=ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE,
        )
        with patch(
            'domains.administrative.tasks.virtual_meeting_email_tasks.send_virtual_meeting_recipient_email',
        ) as mock_recipient:
            count = VirtualMeetingEmailService.dispatch_recipients(task.pk)
        assert count == 1
        mock_recipient.delay.assert_called_once_with(recipient_id=task.recipients.first().pk)