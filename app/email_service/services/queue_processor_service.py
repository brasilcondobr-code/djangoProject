import logging
from datetime import datetime
from django.db import transaction, models
from django.utils import timezone
from email_service.models import ShippingQueue, ConnectionStatus
from email_service.services.provider_router_service import ProviderRouterService
from email_service.services.retry_service import RetryService
from email_service.utils.json_log_builder import JsonLogBuilder

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
        from email_service.models import ShippingQueue
        
        # Buscar itens que precisam de processamento:
        # 1. Estão ativos
        # 2. O status é um status de "pendente" (precisamos verificar isso)
        # 3. O horário agendado já passou (ou é agora)
        # 4. Não foi enviado ainda
        # 5. Se houver tentativa de retry, o próximo horário de tentativa já passou
        
        pending_items = ShippingQueue.objects.filter(
            is_active=True
        ).exclude(
            sent_at__isnull=False
        ).filter(
            models.Q(scheduled_at__lte=timezone.now()) | models.Q(scheduled_at__isnull=True)
        ).filter(
            models.Q(next_retry_at__lte=timezone.now()) | models.Q(next_retry_at__isnull=True)
        )

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
        from email_service.models import ShippingQueue
        
        # Usamos transação atômica para garantir que o status e auditoria sejam atualizados juntos
        with transaction.atomic():
            # Recarrega o item para evitar race conditions
            item = ShippingQueue.objects.select_for_update().get(pk=queue_item.pk)
            
            # 1. Validações iniciais de negócio
            if not item.is_active:
                return {"success": False, "message": "Item inativo."}
            
            # Verificar se já foi enviado
            if item.sent_at:
                return {"success": False, "message": "Item já foi enviado."}

            # Iniciar processamento
            item.processing_started_at = timezone.now()
            item.save()

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
            new_provider_res_str = str(new_provider_res_data)
            if item.provider_response:
                item.provider_response = f"{item.provider_response}\n[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] {new_provider_res_str}"
            else:
                item.provider_response = f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] {new_provider_res_str}"

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
                
                # Histórico de erro (se houver um erro anterior, apenas limpamos ou mantemos? 
                # O usuário quer histórico de erros, então vamos apenas limpar o erro atual 
                # mas manter o histórico no campo de logs)
                item.last_error_message = ""
                logger.info(f"Item {item.uuid} enviado com sucesso.")
            else:
                # FALHA
                error_msg = result.get("error", "Erro desconhecido")
                timestamp_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # --- Lógica de Histórico para Last Error Message ---
                if item.last_error_message:
                    item.last_error_message = f"{item.last_error_message}\n[{timestamp_str}] {error_msg}"
                else:
                    item.last_error_message = f"[{timestamp_str}] {error_msg}"

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
            item.save()

            return {
                "success": result["success"],
                "message": result.get("error") or "Processamento concluído."
            }


