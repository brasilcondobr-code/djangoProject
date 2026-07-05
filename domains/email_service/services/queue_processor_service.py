import logging
from datetime import datetime
from django.db import transaction, models
from django.utils import timezone
from domains.email_service.models import ShippingQueue, ConnectionStatus
from domains.email_service.services.provider_router_service import ProviderRouterService
from domains.email_service.services.retry_service import RetryService
from domains.email_service.utils.json_log_builder import JsonLogBuilder
from domains.email_service.repositories.queue_repository import QueueRepository
from domains.email_service.selectors.queue_selector import ShippingQueueSelector

logger = logging.getLogger(__name__)


class QueueProcessorService:
    """
    Orquestrador do processamento da fila.
    """

    @staticmethod
    def process_queue():
        """
        Processa os itens pendentes da fila.
        """
        pending_items = ShippingQueueSelector.get_pending_emails()

        processed_count = 0
        for item in pending_items:
            QueueProcessorService.process_single_item(item)
            processed_count += 1
        
        return processed_count

    @staticmethod
    def process_single_item(queue_item, user=None):
        """
        Processa um único item da fila de forma atômica.
        """
        with transaction.atomic():
            # 1. Recarrega o item com lock para evitar race conditions
            item = QueueRepository.get_for_update(queue_item.pk)
            
            # Incrementa a tentativa e salva imediatamente para garantir que a ação seja registrada
            item.retry_count += 1
            QueueRepository.save(item)
            
            # 2. Validações iniciais de negócio
            if not item.is_active:
                return {"success": False, "message": "Item inativo."}
            
            # Verificar se já foi enviado
            if item.sent_at:
                return {"success": False, "message": "Item já foi enviado."}

            # Iniciar processamento
            item.processing_started_at = timezone.now()
            
            # Garantir que logs seja uma lista e adicionar log de início
            current_logs = item.logs if isinstance(item.logs, list) else []
            current_logs.append(JsonLogBuilder.build_event("processing_started", "Iniciando processamento do envio"))

            # 3. Executar o envio
            result = ProviderRouterService.route_and_send(item)
            
            # 4. Atualizar Auditoria e Status
            item.response_time_ms = result.get("response_time_ms", 0)
            
            # Mesclar logs do service
            service_logs = result.get("logs", [])
            if isinstance(service_logs, list):
                current_logs.extend(service_logs)
            item.logs = current_logs

            # Tratar resposta do provedor
            provider_res_data = result.get("provider_response", {})
            if provider_res_data:
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                res_str = str(provider_res_data)
                if item.provider_response:
                    item.provider_response = f"{item.provider_response}\n[{timestamp}] {res_str}"
                else:
                    item.provider_response = f"[{timestamp}] {res_str}"
            
            if result["success"]:
                # SUCESSO
                sent_status = ConnectionStatus.objects.filter(status__iexact="Enviado").first()
                if sent_status:
                    item.status = sent_status
                
                item.sent_at = timezone.now()
                item.last_error_message = ""
                logger.info(f"Item {item.uuid} enviado com sucesso.")
            else:
                # FALHA
                error_msg = result.get("error", "Erro desconhecido")
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Atualizar último erro
                if item.last_error_message:
                    item.last_error_message = f"{item.last_error_message}\n[{timestamp}] {error_msg}"
                else:
                    item.last_error_message = f"[{timestamp}] {error_msg}"

                # Verificar se deve tentar novamente
                if RetryService.should_retry(item):
                    retry_status = ConnectionStatus.objects.filter(status__iexact="Retentativa").first()
                    if retry_status:
                        item.status = retry_status
                    
                    item.next_retry_at = RetryService.calculate_next_retry(item.retry_count)
                    logger.warning(f"Item {item.uuid} falhou. Tentativa {item.retry_count}. Próxima em {item.next_retry_at}")
                else:
                    # Falha definitiva
                    item.is_active = False
                    failed_status = ConnectionStatus.objects.filter(status__iexact="Falha").first()
                    if failed_status:
                        item.status = failed_status
                    logger.error(f"Item {item.uuid} atingiu limite de tentativas.")

            item.processing_started_at = None
            QueueRepository.save(item)

            return {
                "success": result["success"],
                "message": result.get("error") or "Processamento concluído."
            }

    @staticmethod
    def reprocess_queue(queryset):
        """
        Reseta os itens da fila para reprocessamento.
        """
        QueueRepository.reset_for_reprocessing(queryset)

    @staticmethod
    def cancel_queue(queryset):
        """
        Cancela os itens da fila.
        """
        QueueRepository.cancel(queryset)
