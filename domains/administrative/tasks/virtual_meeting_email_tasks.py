from celery import shared_task

from domains.email_service.services.queue_processor_service import QueueProcessorService


@shared_task(bind=True, max_retries=3)
def process_virtual_meeting_email_task(self, virtual_meeting_id):
    """
    Dispara o processamento da fila de envio dos convites de uma
    assembleia virtual. A fila é a mesma do módulo de e-mail
    (ShippingQueue) e é processada pelo worker Celery.
    """
    try:
        count = QueueProcessorService.process_queue()
        return f'Processed {count} emails for virtual meeting {virtual_meeting_id}.'
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)