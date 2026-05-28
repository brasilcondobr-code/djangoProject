import logging
import re
import time
from django.core.mail import get_connection
from email_service.utils.response_time import ResponseTime
from email_service.utils.provider_response_parser import ProviderResponseParser
from email_service.utils.json_log_builder import JsonLogBuilder

logger = logging.getLogger(__name__)

def is_valid_email(email):
    if not email:
        return False
    # Regex simples para validar formato de e-mail
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class EmailSenderService:
    """
    Responsável pelo envio físico do e-mail.
    """

    @staticmethod
    def send_smtp(smtp_config, subject, message, to_email, cc=None, bcc=None, reply_to=None, html_message=None):
        """
        Executa o envio via SMTP.
        """
        start_time = ResponseTime.start()
        logs = []
        logs.append(JsonLogBuilder.build_event("smtp_connection_start", "Iniciando conexão SMTP"))
        
        connection = None
        try:
            # VALIDAÇÃO DO REMETENTE (Causa provável do erro 501)
            if not smtp_config.username or not is_valid_email(smtp_config.username):
                error_msg = f"O endereço de remetente ('{smtp_config.username}') é inválido. O campo 'Nome de Usuário' na configuração SMTP deve ser um e-mail completo (ex: usuario@dominio.com)."
                logs.append(JsonLogBuilder.build_event("smtp_validation_error", error_msg))
                return {
                    "success": False,
                    "provider_response": {},
                    "provider_message_id": "",
                    "response_time_ms": ResponseTime.end(start_time),
                    "logs": logs,
                    "error": error_msg
                }

            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=smtp_config.smtp_host,
                port=smtp_config.smtp_port,
                username=smtp_config.username,
                password=smtp_config.password,
                use_tls=smtp_config.use_tls,
                use_ssl=smtp_config.use_ssl,
                timeout=smtp_config.connection_timeout
            )
            connection.open()
            logs.append(JsonLogBuilder.build_event("smtp_connection_success", "Conexão SMTP aberta"))

            recipient_list = [to_email]
            if cc:
                recipient_list.extend([e.strip() for e in cc.split(',') if e.strip()])
            if bcc:
                recipient_list.extend([e.strip() for e in bcc.split(',') if e.strip()])

            from django.core.mail import send_mail
            result = send_mail(
                subject=subject,
                message=message,
                from_email=smtp_config.username,
                recipient_list=recipient_list,
                connection=connection,
                html_message=html_message
            )

            duration = ResponseTime.end(start_time)
            logs.append(JsonLogBuilder.build_event("email_sent", f"E-mail enviado com sucesso ({result} mensagens)"))

            return {
                "success": True,
                "provider_response": {
                    "provider": smtp_config.smtp_host,
                    "response_code": 250,
                    "response_message": "OK",
                    "server_response": "250 2.0.0 OK"
                },
                "provider_message_id": "", 
                "response_time_ms": duration,
                "logs": logs,
                "error": None
            }

        except Exception as e:
            duration = ResponseTime.end(start_time)
            error_msg = str(e)
            logs.append(JsonLogBuilder.build_event("smtp_error", error_msg))
            logger.error(f"Erro no EmailSenderService (SMTP) para {to_email}: {error_msg}")
            
            return {
                "success": False,
                "provider_response": {},
                "provider_message_id": "",
                "response_time_ms": duration,
                "logs": logs,
                "error": error_msg
            }
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass
