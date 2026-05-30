from domains.email_service.models import ShippingQueue

class QueueRepository:
    @staticmethod
    def get_by_id(queue_id):
        return ShippingQueue.objects.get(pk=queue_id)

    @staticmethod
    def get_for_update(queue_id):
        return ShippingQueue.objects.select_for_update().get(pk=queue_id)

    @staticmethod
    def save(queue_item):
        queue_item.save()

    @staticmethod
    def reset_for_reprocessing(queryset):
        for item in queryset:
            item.is_active = True
            item.retry_count = 0
            item.next_retry_at = None
            item.save()

    @staticmethod
    def cancel(queryset):
        queryset.update(is_active=False)
