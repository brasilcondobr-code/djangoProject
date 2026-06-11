from celery import shared_task
from domains.email_service.services.queue_processor_service import QueueProcessorService
from domains.email_service.repositories.queue_repository import QueueRepository

@shared_task(bind=True, max_retries=3)
def process_email_queue_task(self):
    """
    Task to process the entire pending email queue.
    """
    try:
        count = QueueProcessorService.process_queue()
        return f"Processed {count} emails."
    except Exception as exc:
        # Retry on exception
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def process_single_email_task(self, queue_id):
    """
    Task to process a single email from the queue.
    """
    try:
        item = QueueRepository.get_by_id(queue_id)
        result = QueueProcessorService.process_single_item(item)
        if not result["success"]:
             # If it failed but it's a transient error, we might want to retry.
             # For now, we just return the error.
             return f"Failed: {result['message']}"
        return f"Success: {result['message']}"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
