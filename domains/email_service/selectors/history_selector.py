from domains.email_service.models import ShippingQueue

class HistorySelector:
    @staticmethod
    def get_history_for_queue(queue_id):
        return ShippingQueue.objects.get(pk=queue_id)
