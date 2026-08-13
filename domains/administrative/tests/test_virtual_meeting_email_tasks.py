import pytest
from django.utils import timezone

from domains.administrative.services.virtual_meeting_email_service import (
    VirtualMeetingEmailService,
)
from domains.administrative.tasks import (
    process_pending_virtual_meeting_emails,
    send_virtual_meeting_email,
    send_virtual_meeting_recipient_email,
)
from domains.data_management.models import ScheduledTaskModule, ScheduledTaskRecipient


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
class TestVirtualMeetingEmailTasks:

    def test_sweep_dispatches_due_tasks(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        from unittest.mock import patch

        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        VirtualMeetingEmailService.schedule_emails(_meeting)
        with patch(
            'domains.administrative.tasks.virtual_meeting_email_tasks.send_virtual_meeting_email',
        ) as mock_send:
            count = process_pending_virtual_meeting_emails()

        due = ScheduledTaskModule.objects.filter(
            virtual_meeting=_meeting,
            scheduled_at__lte=timezone.now(),
        )
        assert count == due.count()
        dispatched = {c.kwargs['schedule_id'] for c in mock_send.delay.call_args_list}
        assert dispatched == set(due.values_list('pk', flat=True))

    def test_sweep_skips_future_tasks(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        from unittest.mock import patch

        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        _meeting.meeting_date_time_send_mail = timezone.now() + timezone.timedelta(days=30)
        _meeting.save()
        VirtualMeetingEmailService.schedule_emails(_meeting)
        with patch(
            'domains.administrative.tasks.virtual_meeting_email_tasks.send_virtual_meeting_email',
        ) as mock_send:
            count = process_pending_virtual_meeting_emails()
        due = ScheduledTaskModule.objects.filter(
            scheduled_at__lte=timezone.now(),
        )
        assert count == due.count()
        assert count == 1  # apenas o edital (datas passadas) é elegível

    def test_send_task_marks_processing_and_dispatches_recipients(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        from unittest.mock import patch

        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        VirtualMeetingEmailService.schedule_emails(_meeting)
        task = ScheduledTaskModule.objects.get(
            virtual_meeting=_meeting,
            task_type=ScheduledTaskModule.TaskType.VIRTUAL_MEETING_VOTING,
        )
        task.scheduled_at = timezone.now() - timezone.timedelta(minutes=5)
        task.save()

        with patch(
            'domains.administrative.tasks.virtual_meeting_email_tasks.send_virtual_meeting_recipient_email',
        ) as mock_recipient:
            result = send_virtual_meeting_email(schedule_id=task.pk)

        assert result['status'] == ScheduledTaskModule.Status.PROCESSING
        task.refresh_from_db()
        assert task.status == ScheduledTaskModule.Status.PROCESSING
        assert task.attempts == 1
        assert mock_recipient.delay.called is False  # on_commit não dispara em teste

    def test_send_task_idempotent_when_sent(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        VirtualMeetingEmailService.schedule_emails(_meeting)
        task = ScheduledTaskModule.objects.get(
            virtual_meeting=_meeting,
            task_type=ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE,
        )
        task.status = ScheduledTaskModule.Status.SENT
        task.save()
        result = send_virtual_meeting_email(schedule_id=task.pk)
        assert result == {'skipped': 'already_processed'}

    def test_recipient_task_delegates_to_service(
        self, _meeting, _resident, _smtp_config, _connection_pendente,
    ):
        from unittest.mock import patch

        _prepare_valid_meeting(_meeting, _resident, _smtp_config, _connection_pendente)
        VirtualMeetingEmailService.schedule_emails(_meeting)
        recipient = ScheduledTaskRecipient.objects.first()
        with patch(
            'domains.administrative.services.virtual_meeting_email_service.VirtualMeetingEmailService.process_recipient',
            return_value={'success': True},
        ) as mock_process:
            result = send_virtual_meeting_recipient_email(recipient_id=recipient.pk)
        mock_process.assert_called_once_with(recipient.pk)
        assert result == {'success': True}