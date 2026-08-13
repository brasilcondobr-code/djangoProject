import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from domains.administrative.models import VirtualMeeting
from domains.data_management.models import ScheduledTaskModule
from domains.administrative.admin import (
    VirtualMeetingAdmin,
    VirtualMeetingTopicInline,
    VirtualMeetingParticipantInline,
)
from domains.administrative.forms import (
    VirtualMeetingForm,
    VirtualMeetingTopicForm,
    VirtualMeetingTopicFormSet,
    VirtualMeetingParticipantForm,
)


@pytest.mark.django_db
class TestVirtualMeetingAdmin:

    def setup_method(self):
        self.site = AdminSite()
        self.admin = VirtualMeetingAdmin(VirtualMeeting, self.site)

    def test_admin_registered(self):
        assert self.admin is not None

    def test_admin_form(self):
        assert self.admin.form == VirtualMeetingForm

    def test_admin_media_includes_participants_js(self):
        media = self.admin.media
        assert 'js/virtualmeeting_participants.js' in media._js
        assert 'js/virtual_meeting_admin.js' in media._js

    def test_admin_inlines(self):
        inlines = self.admin.inlines
        assert VirtualMeetingTopicInline in inlines
        assert VirtualMeetingParticipantInline not in inlines

    def test_admin_jazzmin_section_order(self):
        expected = (
            'Principal',
            'Edital de Convocação',
            'Participantes',
            'Pautas',
            'Configurações',
            'Auditoria',
        )
        assert self.admin.jazzmin_section_order == expected

    def test_admin_list_display(self):
        expected = (
            'title', 'condominium', 'meeting_status',
            'meeting_date_time_start', 'notice_meeting_date_time',
            'updated_at',
        )
        assert self.admin.list_display == expected

    def test_admin_list_filter(self):
        expected = ('meeting_status', 'condominium', 'meeting_date_time_start')
        assert self.admin.list_filter == expected

    def test_admin_search_fields(self):
        expected = ('title', 'president', 'secretary', 'condominium__name')
        assert self.admin.search_fields == expected

    def test_admin_readonly_fields(self):
        expected = ('created_by_user_display', 'created_at', 'updated_at', 'status_assembleia', 'email_log')
        assert self.admin.readonly_fields == expected

    def test_admin_fieldsets_tabs(self):
        names = [name for name, _ in self.admin.fieldsets]
        assert 'Principal' in names
        assert 'Edital de Convocação' in names
        assert 'Configurações' in names
        assert 'Auditoria' in names

    def test_admin_principal_fields(self):
        fieldsets = dict(self.admin.fieldsets)
        fields = fieldsets['Principal']['fields']
        for f in ('condominium', 'title', 'voting_type', 'meeting_date_time_start',
                  'meeting_date_time_end', 'meeting_date_time_send_mail',
                  'president', 'secretary'):
            assert f in fields

    def test_admin_participantes_fields(self):
        fieldsets = dict(self.admin.fieldsets)
        fields = fieldsets['Participantes']['fields']
        for f in ('participating_resident', 'participating_groups'):
            assert f in fields
        assert 'participating_vote_unit' not in fields

    def test_admin_configuracoes_fields_has_participating_vote_unit(self):
        fieldsets = dict(self.admin.fieldsets)
        fields = fieldsets['Configurações']['fields']
        assert 'participating_vote_unit' in fields

    def test_admin_configuracoes_fields_has_email_settings(self):
        fieldsets = dict(self.admin.fieldsets)
        fields = fieldsets['Configurações']['fields']
        for field in ('email_smtp_configuration', 'connection_status', 'email_log'):
            assert field in fields

    def test_admin_email_log_is_readonly(self):
        assert 'email_log' in self.admin.readonly_fields

    def test_admin_send_email_field_in_configuracoes_after_email_log(self):
        fieldsets = dict(self.admin.fieldsets)
        config_fields = fieldsets['Configurações']['fields']
        assert 'notice_meeting_send_email_participants' in config_fields
        assert config_fields.index('notice_meeting_send_email_participants') > config_fields.index('email_log')
        edital_fields = fieldsets['Edital de Convocação']['fields']
        assert 'notice_meeting_send_email_participants' not in edital_fields

    def test_admin_has_send_email_action(self):
        assert 'enviar_fila_email' in self.admin.actions

    def test_admin_queryset_select_related(self, _meeting):
        qs = self.admin.get_queryset(None)
        joined = qs.query.select_related
        assert {'condominium', 'meeting_status'} <= set(joined)

    def test_inline_topic_form(self):
        assert VirtualMeetingTopicInline.form == VirtualMeetingTopicForm

    def test_inline_topic_model(self):
        assert VirtualMeetingTopicInline.model._meta.model_name == 'virtualmeetingtopic'

    def test_inline_participant_form(self):
        assert VirtualMeetingParticipantInline.form == VirtualMeetingParticipantForm

    def test_inline_participant_model(self):
        assert VirtualMeetingParticipantInline.model._meta.model_name == 'virtualmeetingparticipant'

    def test_configuracoes_fieldset_uses_status_assembleia(self):
        fieldsets = dict(self.admin.fieldsets)
        fields = fieldsets['Configurações']['fields']
        assert 'status_assembleia' in fields
        assert 'meeting_status' not in fields

    def test_auditoria_fieldset_has_created_by_user_display(self):
        fieldsets = dict(self.admin.fieldsets)
        fields = fieldsets['Auditoria']['fields']
        assert 'created_by_user_display' in fields
        assert fields.index('created_by_user_display') < fields.index('created_at')

    def test_created_by_user_display_renders_disabled_select_with_current_user(self, _condo, _assembly_status, _user):
        from django.test import RequestFactory
        request = RequestFactory().get('/admin/administrative/virtualmeeting/add/')
        request.user = _user
        self.admin.get_readonly_fields(request)
        html = self.admin.created_by_user_display(None)
        assert 'disabled' in html
        assert 'selected' in html
        assert _user.username in html

    def test_status_assembleia_readonly_display(self, _meeting, _assembly_status):
        from domains.administrative.admin import VirtualMeetingAdmin
        _assembly_status.is_pending = True
        _assembly_status.save()
        site_admin = VirtualMeetingAdmin(VirtualMeeting, AdminSite())
        value = site_admin.status_assembleia(_meeting)
        assert _assembly_status.description in value
        assert site_admin.status_assembleia.short_description == 'Status da assembleia'

    def test_save_model_sets_pending_status_on_add(self, _condo, _assembly_status):
        from django.utils import timezone
        from domains.administrative.services.virtual_meeting_service import VirtualMeetingService
        pending = VirtualMeetingService.get_pending_status()
        now = timezone.now()
        obj = VirtualMeeting(
            condominium=_condo,
            title='Assembleia Geral Ordinária',
            president='João',
            secretary='Maria',
            meeting_date_time_start=now + timezone.timedelta(days=1),
            meeting_date_time_end=now + timezone.timedelta(days=2),
            meeting_date_time_voting_begins=now + timezone.timedelta(days=1, hours=1),
            meeting_date_time_voting_end=now + timezone.timedelta(days=1, hours=2),
            meeting_date_time_send_mail=now + timezone.timedelta(days=1),
            notice_meeting_date_time=now - timezone.timedelta(days=1),
        )
        site_admin = VirtualMeetingAdmin(VirtualMeeting, AdminSite())
        site_admin.save_model(request=None, obj=obj, form=None, change=False)
        obj.refresh_from_db()
        assert obj.meeting_status == pending

    def test_save_model_sets_created_by_user_on_add(self, _condo, _assembly_status, _user):
        from django.utils import timezone
        now = timezone.now()
        obj = VirtualMeeting(
            condominium=_condo,
            title='Assembleia Geral Ordinária',
            president='João',
            secretary='Maria',
            meeting_date_time_start=now + timezone.timedelta(days=1),
            meeting_date_time_end=now + timezone.timedelta(days=2),
            meeting_date_time_voting_begins=now + timezone.timedelta(days=1, hours=1),
            meeting_date_time_voting_end=now + timezone.timedelta(days=1, hours=2),
            meeting_date_time_send_mail=now + timezone.timedelta(days=1),
            notice_meeting_date_time=now - timezone.timedelta(days=1),
        )
        request = type('Request', (), {'user': _user})()
        site_admin = VirtualMeetingAdmin(VirtualMeeting, AdminSite())
        site_admin.save_model(request=request, obj=obj, form=None, change=False)
        obj.refresh_from_db()
        assert obj.created_by_user == _user

    def test_admin_datetime_fields_are_single_datetime_input(self, _condo, _assembly_status, _user):
        from django.test import RequestFactory
        request = RequestFactory().get('/admin/administrative/virtualmeeting/add/')
        request.user = _user
        form_cls = self.admin.get_form(request=request)
        form = form_cls()
        datetime_names = (
            'meeting_date_time_start', 'meeting_date_time_end',
            'meeting_date_time_voting_begins', 'meeting_date_time_voting_end',
            'notice_meeting_date_time',
        )
        from django.forms import DateTimeField
        from django.forms.widgets import DateTimeInput
        for name in datetime_names:
            field = form.fields[name]
            assert isinstance(field, DateTimeField), name
            assert isinstance(field.widget, DateTimeInput), name

    def test_admin_add_view_renders_notice_meeting_title(self, _condo, _assembly_status, _user):
        from django.test import Client
        _user.is_staff = True
        _user.is_superuser = True
        _user.save()
        client = Client(HTTP_HOST='localhost')
        client.force_login(_user)
        resp = client.get('/admin/administrative/virtualmeeting/add/')
        assert resp.status_code == 200
        html = resp.content.decode()
        assert 'id_notice_meeting_title' in html
        assert 'Título do Edital de Convocação' in html
        assert 'id_meeting_date_time_send_mail' in html
        assert 'Data/Hora - Envio do E-mail' in html

    def test_admin_add_view_creates_with_created_by_user(
        self, _condo, _assembly_status, _user, _resident_type, _resident,
        _smtp_config, _connection_pendente,
    ):
        from django.test import Client
        from django.utils import timezone
        _user.is_staff = True
        _user.is_superuser = True
        _user.save()
        _resident.type_of_resident = _resident_type
        _resident.save()
        client = Client(HTTP_HOST='localhost')
        client.force_login(_user)
        now = timezone.now()
        start = now + timezone.timedelta(days=1)
        end = now + timezone.timedelta(days=2)
        data = {
            'condominium': _condo.pk,
            'title': 'Assembleia via admin',
            'description': '<p>Descrição da assembleia</p>',
            'president': 'João',
            'secretary': 'Maria',
            'meeting_date_time_start': start.strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_end': end.strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_voting_begins': (start + timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_voting_end': (end - timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_send_mail': now.strftime('%Y-%m-%dT%H:%M'),
            'notice_meeting_title': 'Edital de Convocação',
            'notice_meeting_date_time': (now - timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'notice_meeting_description': '<p>Descrição do edital</p>',
            'meeting_status': _assembly_status.pk,
            'participating_groups': _resident_type.pk,
            'participating_resident': [_resident.pk],
            'email_smtp_configuration': _smtp_config.pk,
            'connection_status': _connection_pendente.pk,
            'topics-TOTAL_FORMS': '1',
            'topics-INITIAL_FORMS': '0',
            'topics-MIN_NUM_FORMS': '0',
            'topics-MAX_NUM_FORMS': '1000',
            'topics-0-title': '',
            'topics-0-description': '',
            'topics-0-id': '',
            'topics-0-virtual_meeting': '',
        }
        resp = client.post('/admin/administrative/virtualmeeting/add/', data)
        assert resp.status_code == 302
        vm = VirtualMeeting.objects.get(title='Assembleia via admin')
        assert vm.created_by_user == _user

    def test_admin_add_view_saves_participants(
        self, _condo, _assembly_status, _user, _resident_type, _resident,
        _smtp_config, _connection_pendente,
    ):
        from django.test import Client
        from django.utils import timezone
        _user.is_staff = True
        _user.is_superuser = True
        _user.save()
        _resident.type_of_resident = _resident_type
        _resident.save()
        client = Client(HTTP_HOST='localhost')
        client.force_login(_user)
        now = timezone.now()
        start = now + timezone.timedelta(days=1)
        end = now + timezone.timedelta(days=2)
        data = {
            'condominium': _condo.pk,
            'title': 'Assembleia com participantes',
            'description': '<p>Descrição da assembleia</p>',
            'president': 'João',
            'secretary': 'Maria',
            'meeting_date_time_start': start.strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_end': end.strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_voting_begins': (start + timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_voting_end': (end - timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_send_mail': now.strftime('%Y-%m-%dT%H:%M'),
            'notice_meeting_title': 'Edital de Convocação',
            'notice_meeting_date_time': (now - timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'notice_meeting_description': '<p>Descrição do edital</p>',
            'meeting_status': _assembly_status.pk,
            'participating_groups': _resident_type.pk,
            'participating_resident': [_resident.pk],
            'email_smtp_configuration': _smtp_config.pk,
            'connection_status': _connection_pendente.pk,
            'topics-TOTAL_FORMS': '1',
            'topics-INITIAL_FORMS': '0',
            'topics-MIN_NUM_FORMS': '0',
            'topics-MAX_NUM_FORMS': '1000',
            'topics-0-title': '',
            'topics-0-description': '',
            'topics-0-id': '',
            'topics-0-virtual_meeting': '',
        }
        resp = client.post('/admin/administrative/virtualmeeting/add/', data)
        assert resp.status_code == 302
        vm = VirtualMeeting.objects.get(title='Assembleia com participantes')
        assert vm.participating_groups == _resident_type
        assert list(vm.participating_resident.all()) == [_resident]

    def test_admin_add_view_saves_topics_without_valueerror(
        self, _condo, _assembly_status, _user, _resident_type, _resident,
        _smtp_config, _connection_pendente,
    ):
        from django.test import Client
        from django.utils import timezone
        _user.is_staff = True
        _user.is_superuser = True
        _user.save()
        _resident.type_of_resident = _resident_type
        _resident.save()
        client = Client(HTTP_HOST='localhost')
        client.force_login(_user)
        now = timezone.now()
        start = now + timezone.timedelta(days=1)
        end = now + timezone.timedelta(days=2)
        data = {
            'condominium': _condo.pk,
            'title': 'Assembleia com pautas',
            'description': '<p>Descrição da assembleia</p>',
            'president': 'João',
            'secretary': 'Maria',
            'meeting_date_time_start': start.strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_end': end.strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_voting_begins': (start + timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_voting_end': (end - timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_send_mail': now.strftime('%Y-%m-%dT%H:%M'),
            'notice_meeting_title': 'Edital de Convocação',
            'notice_meeting_date_time': (now - timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'notice_meeting_description': '<p>Descrição do edital</p>',
            'meeting_status': _assembly_status.pk,
            'participating_groups': _resident_type.pk,
            'participating_resident': [_resident.pk],
            'email_smtp_configuration': _smtp_config.pk,
            'connection_status': _connection_pendente.pk,
            'topics-TOTAL_FORMS': '1',
            'topics-INITIAL_FORMS': '0',
            'topics-MIN_NUM_FORMS': '0',
            'topics-MAX_NUM_FORMS': '1000',
            'topics-0-title': 'Vestibulum at ipsum magna',
            'topics-0-description': 'Descrição da pauta',
            'topics-0-id': '',
            'topics-0-virtual_meeting': '',
        }
        resp = client.post('/admin/administrative/virtualmeeting/add/', data)
        assert resp.status_code == 302
        vm = VirtualMeeting.objects.get(title='Assembleia com pautas')
        assert list(vm.topics.values_list('title', flat=True)) == ['Vestibulum at ipsum magna']

    def test_admin_add_view_rejects_duplicate_topic_titles(
        self, _condo, _assembly_status, _user, _resident_type, _resident,
        _smtp_config, _connection_pendente,
    ):
        from django.test import Client
        from django.utils import timezone
        _user.is_staff = True
        _user.is_superuser = True
        _user.save()
        _resident.type_of_resident = _resident_type
        _resident.save()
        client = Client(HTTP_HOST='localhost')
        client.force_login(_user)
        now = timezone.now()
        start = now + timezone.timedelta(days=1)
        end = now + timezone.timedelta(days=2)
        data = {
            'condominium': _condo.pk,
            'title': 'Assembleia pautas duplicadas',
            'description': '<p>Descrição da assembleia</p>',
            'president': 'João',
            'secretary': 'Maria',
            'meeting_date_time_start': start.strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_end': end.strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_voting_begins': (start + timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_voting_end': (end - timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'meeting_date_time_send_mail': now.strftime('%Y-%m-%dT%H:%M'),
            'notice_meeting_title': 'Edital de Convocação',
            'notice_meeting_date_time': (now - timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'notice_meeting_description': '<p>Descrição do edital</p>',
            'meeting_status': _assembly_status.pk,
            'participating_groups': _resident_type.pk,
            'participating_resident': [_resident.pk],
            'email_smtp_configuration': _smtp_config.pk,
            'connection_status': _connection_pendente.pk,
            'topics-TOTAL_FORMS': '2',
            'topics-INITIAL_FORMS': '0',
            'topics-MIN_NUM_FORMS': '0',
            'topics-MAX_NUM_FORMS': '1000',
            'topics-0-title': 'Pauta repetida',
            'topics-0-description': '',
            'topics-0-id': '',
            'topics-0-virtual_meeting': '',
            'topics-1-title': 'PAUTA REPETIDA',
            'topics-1-description': '',
            'topics-1-id': '',
            'topics-1-virtual_meeting': '',
        }
        resp = client.post('/admin/administrative/virtualmeeting/add/', data)
        assert resp.status_code == 200
        assert 'Já existe uma pauta com este título nesta assembleia.' in resp.content.decode()
        assert not VirtualMeeting.objects.filter(title='Assembleia pautas duplicadas').exists()

    def test_inline_topic_formset_is_registered(self):
        assert VirtualMeetingTopicInline.formset is not None

    def test_admin_action_queues_emails_and_logs(
        self, _meeting, _user, _resident, _smtp_config, _connection_pendente, _connection_enviado,
    ):
        from unittest.mock import patch
        from django.test import Client

        _user.is_staff = True
        _user.is_superuser = True
        _user.save()
        _meeting.description = 'Descrição da assembleia'
        _meeting.notice_meeting_title = 'Edital de Convocação'
        _meeting.notice_meeting_description = 'Descrição do edital'
        _meeting.notice_meeting_send_email_participants = True
        _meeting.email_smtp_configuration = _smtp_config
        _meeting.connection_status = _connection_pendente
        _meeting.save()
        _meeting.participating_resident.add(_resident)

        client = Client(HTTP_HOST='localhost')
        client.force_login(_user)
        resp = client.post('/admin/administrative/virtualmeeting/', {
            'action': 'enviar_fila_email',
            '_selected_action': [str(_meeting.pk)],
        })
        assert resp.status_code == 302
        schedules = ScheduledTaskModule.objects.filter(virtual_meeting=_meeting)
        assert schedules.count() == 2
        for schedule in schedules:
            assert schedule.recipients.filter(resident=_resident).exists()
        _meeting.refresh_from_db()
        assert 'Agendamento criado: Edital de Convocação' in _meeting.email_log
        assert 'Agendamento criado: Convocação para Votação' in _meeting.email_log
        assert _meeting.connection_status.status.lower() == 'enviado'

    def test_admin_action_reports_missing_fields(self, _meeting, _user):
        from django.test import Client

        _user.is_staff = True
        _user.is_superuser = True
        _user.save()
        client = Client(HTTP_HOST='localhost')
        client.force_login(_user)
        resp = client.post('/admin/administrative/virtualmeeting/', {
            'action': 'enviar_fila_email',
            '_selected_action': [str(_meeting.pk)],
        })
        assert resp.status_code == 302
        assert ScheduledTaskModule.objects.filter(
            virtual_meeting=_meeting,
        ).count() == 0
        _meeting.refresh_from_db()
        assert _meeting.email_log == ''

    def test_admin_change_view_renders_participants(self, _meeting, _user, _resident_type, _resident):
        from django.test import Client
        _user.is_staff = True
        _user.is_superuser = True
        _user.save()
        _resident.type_of_resident = _resident_type
        _resident.save()
        _meeting.participating_groups = _resident_type
        _meeting.save()
        _meeting.participating_resident.add(_resident)
        client = Client(HTTP_HOST='localhost')
        client.force_login(_user)
        resp = client.get(f'/admin/administrative/virtualmeeting/{_meeting.pk}/change/')
        assert resp.status_code == 200
        html = resp.content.decode()
        assert 'virtualmeeting_participants.js' in html
        assert 'id_participating_groups' in html
        assert 'id_participating_resident' in html
        assert f'value="{_resident_type.pk}" selected' in html