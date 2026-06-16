from django.db import models
from django.utils import timezone
from domains.email_service.models import ShippingQueue

class ShippingQueueSelector:
    @staticmethod
    def get_pending_emails():
        return ShippingQueue.objects.filter(
            is_active=True
        ).exclude(
            sent_at__isnull=False
        ).filter(
            models.Q(scheduled_at__lte=timezone.now()) | models.Q(scheduled_at__isnull=True)
        ).filter(
            models.Q(next_retry_at__lte=timezone.now()) | models.Q(next_retry_at__isnull=True)
        )
