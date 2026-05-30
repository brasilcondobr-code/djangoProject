from domains.email_service.models import ShippingQueue

class HistoryRepository:
    @staticmethod
    def append_error(queue_id, error_message):
        from datetime import datetime
        from django.utils import timezone
        item = ShippingQueue.objects.get(pk=queue_id)
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        if item.last_error_message:
            item.last_error_message = f"{item.last_error_message}\n[{timestamp}] {error_message}"
        else:
            item.last_error_message = f"[{timestamp}] {error_message}"
        item.save()

    @staticmethod
    def append_provider_response(queue_id, response_data):
        from datetime import datetime
        from django.utils import timezone
        item = ShippingQueue.objects.get(pk=queue_id)
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        response_str = str(response_data)
        if item.provider_response:
            item.provider_response = f"{item.provider_response}\n[{timestamp}] {response_str}"
        else:
            item.provider_response = f"[{timestamp}] {response_str}"
        item.save()
