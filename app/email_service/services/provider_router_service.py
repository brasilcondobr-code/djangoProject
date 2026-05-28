import logging
from email_service.services.email_sender_service import EmailSenderService

logger = logging.getLogger(__name__)

class ProviderRouterService:
    """
    Responsável por decidir qual provedor utilizar.
    """

    @staticmethod
    def route_and_send(queue_item):
        """
        Roteia o item da fila para o provedor correto e executa o envio.
        """
        smtp_config = queue_item.smtp_configuration
        
        if not smtp_config:
            return {
                "success": False,
                "provider_response": {},
                "provider_message_id": "",
                "response_time_ms": 0,
                "logs": [{"event": "routing_error", "message": "Sem configuração SMTP"}],
                "error": "Sem configuração SMTP"
            }

        # Por enquanto, implementamos apenas o roteamento para SMTP
        # Mas a estrutura permite adicionar SendGrid, Mailgun, etc.
        
        if smtp_config.api_supported:
            # TODO: Implementar EmailSenderService.send_api
            return {
                "success": False,
                "provider_response": {},
                "provider_message_id": "",
                "response_time_ms": 0,
                "logs": [{"event": "routing_error", "message": "API não implementada"}],
                "error": "API não implementada"
            }
        else:
            return EmailSenderService.send_smtp(
                smtp_config=smtp_config,
                subject=queue_item.subject,
                message=queue_item.message,
                to_email=queue_item.to_email,
                cc=queue_item.cc,
                bcc=queue_item.bcc,
                reply_to=queue_item.reply_to,
                html_message=queue_item.html_message
            )
