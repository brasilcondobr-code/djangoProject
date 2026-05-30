import logging
from datetime import datetime
from django.db import transaction, models
from django.utils import timezone
from domains.email_service.models import ShippingQueue, ConnectionStatus
from domains.email_service.services.provider_router_service import ProviderRouterService
from domains.email_service.services.retry_service import RetryService
from domains.email_service.utils.json_log_builder import JsonLogBuilder
from domains.email_service.repositories.queue_repository import QueueRepository
from domains.email_service.repositories.history_repository import HistoryRepository
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
        # Usamos transação atômica para garantir que o status e auditoria sejam atualizados juntos
        with transaction.atomic():
            # Recarrega o item para evitar race conditions usando o Repository
            item = QueueRepository.get_for_update(queue_item.pk)
            
            # 1. Validações iniciais de negócio
            if not item.is_active:
                return {"success": False, "message": "Item inativo."}
            
            # Verificar se já foi enviado
            if item.sent_at:
                return {"success": False, "message": "Item já foi enviado."}

            # Iniciar processamento
            item.processing_started_at = timezone.now()
            QueueRepository.save(item)

            # Garantir que logs seja uma lista para histórico
            current_logs = item.logs if isinstance(item.logs, list) else []
            processing_log = JsonLogBuilder.build_event("processing_started", "Iniciando processamento do envio")
            current_logs.append(processing_log)

            # 2. Executar o envio
            result = ProviderRouterService.route_and_send(item)
            
            # 3. Atualizar Auditoria e Status
            item.response_time_ms = result.get("response_time_ms", 0)
            
            # --- Lógica de Histórico para Provider Response ---
            new_provider_res_data = result.get("provider_response", {})
            HistoryRepository.append_provider_response(item.pk, new_provider_res_data)
            
            # Atualiza o objeto em memória para os próximos passos
            # (Como HistoryRepository faz um save, precisamos recarregar ou atualizar o objeto local)
            item = QueueRepository.get_by_id(item.pk)
            item.provider_response = item.provider_response # already updated by repository

            item.provider_message_id = result.get("provider_message_id", "")
            
            # Mesclar logs do service com logs locais
            service_logs = result.get("logs", [])
            if isinstance(service_logs, list):
                current_logs.extend(service_logs)
            
            # Atualizar o campo logs com a lista completa
            item.logs = current_logs

            if result["success"]:
                # SUCESSO
                # Procurar status 'Enviado' (ou similar)
                sent_status = ConnectionStatus.objects.filter(status__iexact="Enviado").first()
                if sent_status:
                    item.status = sent_status
                
                item.sent_at = timezone.now()
                
                # Histórico de erro (limpamos o erro atual pois foi sucesso)
                item.last_error_message = ""
                logger.info(f"Item {item.uuid} enviado com sucesso.")
            else:
                # FALHA
                error_msg = result.get("error", "Erro desconhecido")
                HistoryRepository.append_error(item.pk, error_msg)
                
                # Recarrega para ter o erro atualizado
                item = QueueRepository.get_by_id(item.pk)
                item.last_error_message = item.last_error_message # already updated by repository

                # Verificar se deve tentar novamente
                if RetryService.should_retry(item):
                    item.retry_count += 1
                    
                    # Procurar status 'Retentativa'
                    retry_status = ConnectionStatus.objects.filter(status__iexact="Retentativa").first()
                    if retry_status:
                        item.status = retry_status
                    
                    item.next_retry_at = RetryService.calculate_next_retry(item.retry_count)
                    logger.warning(f"Item {item.uuid} falhou. Tentativa {item.retry_count}. Próxima em {item.next_retry_at}")
                else:
                    # Falha definitiva
                    item.is_active = False
                    # Procurar status 'Falha'
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




