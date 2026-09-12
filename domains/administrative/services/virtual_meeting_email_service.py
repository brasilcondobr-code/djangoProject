import logging
from html import unescape
from re import sub as re_sub

from django.db import transaction
from django.utils import timezone

from domains.administrative.exceptions import VirtualMeetingValidationException
from domains.data_management.models import ScheduledTaskModule, ScheduledTaskRecipient
from domains.email_service.models import ConnectionStatus, ShippingQueue, SMTPConfiguration

logger = logging.getLogger(__name__)


class VirtualMeetingEmailService:

    EMAIL_TYPES = {
        ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE: {
            'label': 'Edital de Convocação',
            'subject_field': 'notice_meeting_title',
            'content_field': 'notice_meeting_description',
            'scheduled_at_field': 'notice_meeting_date_time',
        },
        ScheduledTaskModule.TaskType.VIRTUAL_MEETING_VOTING: {
            'label': 'Convocação para Votação',
            'subject_field': 'title',
            'content_field': 'description',
            'scheduled_at_field': 'meeting_date_time_send_mail',
        },
    }

    @staticmethod
    def _html_to_text(value):
        if not value:
            return ''
        text = re_sub(r'<[^>]+>', ' ', value)
        text = unescape(text)
        return re_sub(r'\s+', ' ', text).strip()

    @staticmethod
    def build_subject(virtual_meeting, task_type):
        config = VirtualMeetingEmailService.EMAIL_TYPES[task_type]
        title = getattr(virtual_meeting, config['subject_field']) or ''
        if task_type == ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE:
            return f'Edital de Convocação: {title}'
        return f'Convocação para Votação: {title}'

    @staticmethod
    def build_message(virtual_meeting, task_type):
        config = VirtualMeetingEmailService.EMAIL_TYPES[task_type]
        content = getattr(virtual_meeting, config['content_field']) or ''
        if task_type == ScheduledTaskModule.TaskType.VIRTUAL_MEETING_NOTICE:
            prefix = (
                f'Informamos que foi publicado o edital de convocação da '
                f'assembleia "{virtual_meeting.title}".\n\n'
            )
        else:
            prefix = (
                f'Convocamos você a participar da votação da assembleia '
                f'"{virtual_meeting.title}".\n\n'
            )
        return prefix + VirtualMeetingEmailService._html_to_text(content)

    @staticmethod
    def build_html_message(virtual_meeting, task_type):
        config = VirtualMeetingEmailService.EMAIL_TYPES[task_type]
        content = getattr(virtual_meeting, config['content_field']) or ''
        return content

    @staticmethod
    def get_schedule_config(virtual_meeting, task_type):
        config = VirtualMeetingEmailService.EMAIL_TYPES[task_type]
        return {
            'label': config['label'],
            'scheduled_at': getattr(virtual_meeting, config['scheduled_at_field']),
            'subject': VirtualMeetingEmailService.build_subject(virtual_meeting, task_type),
            'message': VirtualMeetingEmailService.build_message(virtual_meeting, task_type),
            'html_message': VirtualMeetingEmailService.build_html_message(
                virtual_meeting, task_type,
            ),
        }

    @staticmethod
    def _collect_residents(virtual_meeting):
        return (
            virtual_meeting.participating_resident.all()
            .filter(email__isnull=False)
            .exclude(email='')
        )

    @staticmethod
    def get_validation_errors(virtual_meeting):
        errors = []

        if not virtual_meeting.condominium_id:
            errors.append('Condomínio')
        if not (virtual_meeting.title or '').strip():
            errors.append('Título')
        if not (virtual_meeting.description or '').strip():
            errors.append('Descrição/conteúdo da assembleia')
        if not virtual_meeting.meeting_date_time_start:
            errors.append('Início da assembleia')
        if not virtual_meeting.meeting_date_time_end:
            errors.append('Término da assembleia')
        if not virtual_meeting.meeting_date_time_voting_begins:
            errors.append('Início da votação')
        if not virtual_meeting.meeting_date_time_voting_end:
            errors.append('Término da votação')
        if not virtual_meeting.meeting_date_time_send_mail:
            errors.append('Data/Hora - Envio do E-mail')

        if not virtual_meeting.notice_meeting_date_time:
            errors.append('Data da convocação')
        if not (virtual_meeting.notice_meeting_title or '').strip():
            errors.append('Título do edital de convocação')
        if not (virtual_meeting.notice_meeting_description or '').strip():
            errors.append('Descrição do edital')

        if not virtual_meeting.participating_resident.exists():
            errors.append('Participantes selecionados')

        if not virtual_meeting.email_smtp_configuration_id:
            errors.append('Configuração SMTP')

        connection_status = virtual_meeting.connection_status
        if connection_status is None:
            errors.append('Email Status (Pendente)')
        elif (connection_status.status or '').strip().lower() != 'pendente':
            errors.append('Email Status (Pendente)')

        return errors

    @staticmethod
    def validate_meeting_for_queue(virtual_meeting):
        errors = VirtualMeetingEmailService.get_validation_errors(virtual_meeting)
        if errors:
            raise VirtualMeetingValidationException(
                'Não é possível agendar o envio de e-mail: '
                f'campos obrigatórios pendentes ({", ".join(errors)}).'
            )

    @staticmethod
    def _append_email_log(virtual_meeting, message):
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f'[{timestamp}] {message}'
        if virtual_meeting.email_log:
            virtual_meeting.email_log = (
                virtual_meeting.email_log.rstrip('\n') + '\n' + entry + '\n'
            )
        else:
            virtual_meeting.email_log = entry + '\n'

    @staticmethod
    @transaction.atomic
    def schedule_emails(virtual_meeting):
        VirtualMeetingEmailService.validate_meeting_for_queue(virtual_meeting)

        if not virtual_meeting.notice_meeting_send_email_participants:
            VirtualMeetingEmailService._append_email_log(
                virtual_meeting,
                'Envio de e-mail desabilitado: campo "Enviar e-mail aos participantes" = Não.',
            )
            virtual_meeting.save(
                update_fields=['email_log', 'updated_at'],
            )
            return {'skipped': True, 'schedules': []}

        residents = VirtualMeetingEmailService._collect_residents(virtual_meeting)
        total_participants = virtual_meeting.participating_resident.count()
        no_email = total_participants - residents.count()

        scheduled = []
        for task_type in ScheduledTaskModule.TaskType:
            config = VirtualMeetingEmailService.get_schedule_config(
                virtual_meeting, task_type,
            )
            task, _created = ScheduledTaskModule.objects.update_or_create(
                virtual_meeting=virtual_meeting,
                task_type=task_type,
                defaults={
                    'scheduled_at': config['scheduled_at'],
                    'status': ScheduledTaskModule.Status.PENDING,
                    'attempts': 0,
                    'last_error': '',
                    'celery_task_id': '',
                },
            )

            recipients_count = 0
            for resident in residents:
                _recipient, created = ScheduledTaskRecipient.objects.get_or_create(
                    task=task,
                    resident=resident,
                    defaults={
                        'email': resident.email,
                        'status': ScheduledTaskRecipient.Status.PENDING,
                    },
                )
                if created:
                    recipients_count += 1

            VirtualMeetingEmailService._append_email_log(
                virtual_meeting,
                f'Agendamento criado: {config["label"]} '
                f'(envio em {config["scheduled_at"]:%d/%m/%Y às %H:%M}) - '
                f'{recipients_count} destinatário(s).',
            )
            scheduled.append({
                'task_type': task_type,
                'task_id': task.pk,
                'recipients': recipients_count,
            })

        status_enviado = ConnectionStatus.objects.filter(
            status__iexact='Enviado',
        ).first()
        if status_enviado is not None:
            virtual_meeting.connection_status = status_enviado
        virtual_meeting.save(
            update_fields=['connection_status', 'email_log', 'updated_at'],
        )

        logger.info(
            'virtual_meeting_email_scheduled',
            extra={
                'virtual_meeting_id': virtual_meeting.pk,
                'schedules': len(scheduled),
                'recipients': sum(s['recipients'] for s in scheduled),
                'no_email': no_email,
                'operation': 'schedule_emails',
            },
        )

        transaction.on_commit(
            VirtualMeetingEmailService.dispatch_pending_schedules,
        )
        return {
            'skipped': False,
            'schedules': scheduled,
            'no_email': no_email,
        }

    @staticmethod
    def dispatch_pending_schedules():
        from domains.administrative.tasks.virtual_meeting_email_tasks import (
            process_pending_virtual_meeting_emails,
        )

        process_pending_virtual_meeting_emails.delay()

    @staticmethod
    def dispatch_recipients(schedule_id):
        from domains.administrative.tasks.virtual_meeting_email_tasks import (
            send_virtual_meeting_recipient_email,
        )

        recipients = ScheduledTaskRecipient.objects.filter(
            task_id=schedule_id,
            status=ScheduledTaskRecipient.Status.PENDING,
        )
        for recipient in recipients:
            send_virtual_meeting_recipient_email.delay(recipient_id=recipient.pk)
        return recipients.count()

    @staticmethod
    @transaction.atomic
    def process_recipient(recipient_id):
        from domains.email_service.services.queue_processor_service import (
            QueueProcessorService,
        )

        recipient = ScheduledTaskRecipient.objects.select_for_update().get(
            pk=recipient_id,
        )
        task = ScheduledTaskModule.objects.select_for_update().get(
            pk=recipient.task_id,
        )
        virtual_meeting = task.virtual_meeting

        if recipient.status == ScheduledTaskRecipient.Status.SENT:
            return {'success': True, 'skipped': 'already_sent'}

        if (
            recipient.status == ScheduledTaskRecipient.Status.CANCELED
            or task.status == ScheduledTaskModule.Status.CANCELED
            or task.status == ScheduledTaskModule.Status.SENT
        ):
            return {'success': True, 'skipped': 'canceled'}

        if not VirtualMeetingEmailService._collect_residents(
            virtual_meeting,
        ).filter(pk=recipient.resident_id).exists():
            recipient.status = ScheduledTaskRecipient.Status.CANCELED
            recipient.save(update_fields=['status', 'updated_at'])
            return {'success': True, 'skipped': 'resident_removed'}

        email = recipient.email or ''
        if not email:
            recipient.status = ScheduledTaskRecipient.Status.FAILED
            recipient.last_error = 'Morador sem e-mail cadastrado.'
            recipient.save(update_fields=['status', 'last_error', 'updated_at'])
            VirtualMeetingEmailService._sync_task_status(task)
            return {'success': False, 'permanent': True, 'message': 'Sem e-mail cadastrado.'}

        config = VirtualMeetingEmailService.get_schedule_config(
            virtual_meeting, task.task_type,
        )
        module_origin = f'virtual_meeting_{task.task_type}'

        smtp_config = virtual_meeting.email_smtp_configuration
        if not smtp_config:
            smtp_config = SMTPConfiguration.objects.filter(is_active=True).first()

        pending_status = ConnectionStatus.objects.filter(
            status__iexact='Pendente',
        ).first()

        queue_item = ShippingQueue.objects.filter(
            module_origin=module_origin,
            reference_id=virtual_meeting.pk,
            to_email=email,
        ).first()
        if not queue_item:
            queue_item = ShippingQueue.objects.create(
                condominium=virtual_meeting.condominium,
                module_origin=module_origin,
                reference_id=virtual_meeting.pk,
                subject=config['subject'],
                to_email=email,
                message=config['message'],
                html_message=config['html_message'],
                smtp_configuration=smtp_config,
                status=pending_status,
                is_active=True,
            )

        result = QueueProcessorService.process_single_item(queue_item)

        if result.get('success'):
            recipient.status = ScheduledTaskRecipient.Status.SENT
            recipient.sent_at = timezone.now()
            recipient.last_error = ''
            log_message = f'Enviado para Filas de Envio/Email: {config["label"]}.'
            logger.info(
                'virtual_meeting_email_sent',
                extra={
                    'virtual_meeting_id': virtual_meeting.pk,
                    'schedule_id': task.pk,
                    'task_type': task.task_type,
                    'recipient_id': recipient.pk,
                    'operation': 'process_recipient',
                },
            )
        else:
            recipient.status = ScheduledTaskRecipient.Status.FAILED
            recipient.last_error = result.get('message', 'Erro desconhecido')
            log_message = (
                f'Falha ao enviar {config["label"]}: '
                f'{recipient.last_error}.'
            )
            logger.error(
                'virtual_meeting_email_failed',
                extra={
                    'virtual_meeting_id': virtual_meeting.pk,
                    'schedule_id': task.pk,
                    'task_type': task.task_type,
                    'recipient_id': recipient.pk,
                    'operation': 'process_recipient',
                },
            )

        recipient.save(
            update_fields=['status', 'sent_at', 'last_error', 'updated_at'],
        )
        VirtualMeetingEmailService._append_email_log(virtual_meeting, log_message)
        VirtualMeetingEmailService._sync_task_status(task)
        virtual_meeting.save(
            update_fields=['email_log', 'updated_at'],
        )
        return result

    @staticmethod
    @transaction.atomic
    def _sync_task_status(task):
        task = ScheduledTaskModule.objects.select_for_update().get(
            pk=task.pk,
        )
        recipients = list(task.recipients.all())
        if not recipients:
            task.status = ScheduledTaskModule.Status.SENT
            task.sent_at = timezone.now()
        elif all(r.status == ScheduledTaskRecipient.Status.SENT for r in recipients):
            task.status = ScheduledTaskModule.Status.SENT
            task.sent_at = timezone.now()
        elif any(
            r.status == ScheduledTaskRecipient.Status.FAILED for r in recipients
        ):
            task.status = ScheduledTaskModule.Status.FAILED
        else:
            task.status = ScheduledTaskModule.Status.PROCESSING
        task.save(update_fields=['status', 'sent_at', 'updated_at'])
