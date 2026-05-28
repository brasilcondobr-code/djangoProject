from datetime import timedelta
from django.utils import timezone

class RetryService:
    """
    Gerencia a lógica de retentativas.
    """

    @staticmethod
    def should_retry(queue_item):
        """
        Verifica se o item deve ser tentado novamente.
        """
        if queue_item.retry_count >= queue_item.max_retry_attempts:
            return False
            
        if queue_item.next_retry_at and queue_item.next_retry_at > timezone.now():
            return False
            
        return True

    @staticmethod
    def calculate_next_retry(retry_count):
        """
        Calcula o tempo de espera baseado no número de tentativas (exponential backoff simples).
        Regra: retry_count * 5 minutos.
        """
        return timezone.now() + timedelta(minutes=retry_count * 5)
