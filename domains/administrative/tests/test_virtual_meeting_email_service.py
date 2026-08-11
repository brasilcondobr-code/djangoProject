import pytest
from domains.administrative.services.virtual_meeting_email_service import (
    VirtualMeetingEmailService,
)
from domains.administrative.exceptions import VirtualMeetingValidationException


@pytest.mark.django_db
class TestVirtualMeetingEmailService:

    def test_build_subject(self, _meeting):
        assert VirtualMeetingEmailService.build_subject(_meeting) == f'Convocação: {_meeting.title}'

    def test_build_message(self, _meeting):
        message = VirtualMeetingEmailService.build_message(_meeting)
        assert _meeting.title in message

    def test_validate_without_participants(self, _meeting):
        _meeting.notice_meeting_send_email_participants = True
        _meeting.save()
        with pytest.raises(VirtualMeetingValidationException):
            VirtualMeetingEmailService.validate_meeting_for_queue(_meeting)

    def test_validate_without_email_flag(self, _meeting, _resident_type, _resident):
        from domains.administrative.services import VirtualMeetingParticipantService
        VirtualMeetingParticipantService.add_participant(_meeting, _resident_type, _resident)
        with pytest.raises(VirtualMeetingValidationException):
            VirtualMeetingEmailService.validate_meeting_for_queue(_meeting)

    def test_validate_ok(self, _meeting, _resident_type, _resident):
        from domains.administrative.services import VirtualMeetingParticipantService
        VirtualMeetingParticipantService.add_participant(_meeting, _resident_type, _resident)
        _meeting.notice_meeting_send_email_participants = True
        _meeting.save()
        assert VirtualMeetingEmailService.validate_meeting_for_queue(_meeting) is None

    def test_queue_notice_email_raises_without_residents(self, _meeting):
        _meeting.notice_meeting_send_email_participants = True
        _meeting.save()
        with pytest.raises(VirtualMeetingValidationException):
            VirtualMeetingEmailService.queue_notice_email(_meeting)

    def test_is_notice_future_past(self, _meeting):
        assert VirtualMeetingEmailService.is_notice_future(_meeting) is False