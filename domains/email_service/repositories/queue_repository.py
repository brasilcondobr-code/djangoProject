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
            item.sent_at = None
            item.last_error_message = ""
            item.provider_response = ""
            item.logs = []
            item.response_time_ms = 0
            # Resetamos o status para Pendente para que ele apareça corretamente na fila
            # (Assumindo que o status 'Pendente' existe, o que verificamos anteriormente)
            from domains.email_service.models import ConnectionStatus
            pendente_status = ConnectionStatus.objects.filter(status__iexact="Pendente").first()
            if pendente_status:
                item.status = pendente_status
            item.save()

    @staticmethod
    def cancel(queryset):
        queryset.update(is_active=False)
