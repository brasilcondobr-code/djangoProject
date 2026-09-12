import logging

from celery import shared_task
from django.utils import timezone

from domains.administrative.services.virtual_meeting_email_service import (
    VirtualMeetingEmailService,
)
from domains.data_management.models import ScheduledTaskModule

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_pending_virtual_meeting_emails(self):
    """
    Varredura periódica (Celery Beat): identifica os agendamentos de e-mail
    cuja data/hora programada já venceu e os coloca na fila de envio.
    """
    due_tasks = ScheduledTaskModule.objects.filter(
        status=ScheduledTaskModule.Status.PENDING,
        scheduled_at__lte=timezone.now(),
        virtual_meeting__isnull=False,
    )
    for task in due_tasks:
        send_virtual_meeting_email.delay(schedule_id=task.pk)
    count = due_tasks.count()
    logger.info(
        'virtual_meeting_email_sweep',
        extra={'schedules': count, 'operation': 'sweep'},
    )
    return count


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def send_virtual_meeting_email(self, schedule_id):
    """
    Processa um agendamento: valida, marca como PROCESSING e despacha uma
    tarefa individual por destinatário pendente.
    """
    from django.db import transaction

    with transaction.atomic():
        task = ScheduledTaskModule.objects.select_for_update().get(
            pk=schedule_id,
        )

        if task.status in (
            ScheduledTaskModule.Status.SENT,
            ScheduledTaskModule.Status.CANCELED,
        ):
            return {'skipped': 'already_processed'}

        if task.status == ScheduledTaskModule.Status.FAILED:
            return {'skipped': 'failed'}

        if task.scheduled_at > timezone.now():
            return {'skipped': 'not_yet_due'}

        task.status = ScheduledTaskModule.Status.PROCESSING
        task.attempts += 1
        task.save(update_fields=['status', 'attempts', 'updated_at'])
        transaction.on_commit(
            lambda: VirtualMeetingEmailService.dispatch_recipients(task.pk),
        )
        return {'schedule_id': task.pk, 'status': task.status}


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def send_virtual_meeting_recipient_email(self, recipient_id):
    """
    Tarefa individual por destinatário: cria/usa a Fila de Envio (ShippingQueue),
    envia pelo provedor SMTP padrão e registra sucesso ou falha.
    """
    result = VirtualMeetingEmailService.process_recipient(recipient_id)
    return result
