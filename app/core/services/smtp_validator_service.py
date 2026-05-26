import time
import logging
import socket
import ssl
from django.core.mail import get_connection
from django.utils import timezone
from django.contrib.auth.models import User
from email_service.models import ConnectionStatus
from .email_test_service import EmailTestService

logger = logging.getLogger(__name__)

class SMTPValidator:

    @staticmethod
    def validate(smtp_config, user=None):
        """
        Validates the SMTP configuration.
        Returns:
            dict: {
                "success": bool,
                "message": str,
                "response_time_ms": int
            }
        """
        start_time = time.time()
        smtp_config.validation_attempts += 1
        smtp_config.last_connection_tested_at = timezone.now()
        smtp_config.last_validated_by = user
        
        try:
            # Etapa 1: Validar se a configuração está ativa
            if not smtp_config.is_active:
                return SMTPValidator._finalize_result(
                    smtp_config, 
                    False, 
                    "Configuração SMTP inativa.", 
                    0,
                    "Inativo"
                )

            # Etapa 2: Validar campos obrigatórios
            error_msg = SMTPValidator._validate_required_fields(smtp_config)
            if error_msg:
                return SMTPValidator._finalize_result(
                    smtp_config, 
                    False, 
                    error_msg, 
                    0
                )

            # Etapa 3: Validar consistência TLS/SSL
            if smtp_config.use_tls and smtp_config.use_ssl:
                return SMTPValidator._finalize_result(
                    smtp_config, 
                    False, 
                    "TLS e SSL não podem ser utilizados simultaneamente.", 
                    0
                )

            # Etapa 4 & 5: Realizar conexão SMTP e Validar autenticação
            connection_success, connection_error = SMTPValidator._test_connection(smtp_config)
            if not connection_success:
                return SMTPValidator._finalize_result(
                    smtp_config, 
                    False, 
                    connection_error, 
                    0
                )

            # Etapa 6: Envio de e-mail teste
            test_email_msg = ""
            if smtp_config.test_email_address:
                email_success, email_msg = EmailTestService.send_test_email(smtp_config)
                if not email_success:
                    test_email_msg = f" | [Aviso: {email_msg}]"
                else:
                    test_email_msg = " | E-mail teste enviado."

            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)

            success_message = f"Conexão SMTP validada com sucesso.{test_email_msg}"
            
            return SMTPValidator._finalize_result(
                smtp_config, 
                True, 
                success_message, 
                response_time_ms,
                "Sucesso"
            )

        except Exception as e:
            error_msg = f"Erro desconhecido: {str(e)}"
            logger.error(f"Erro inesperado ao validar SMTP {smtp_config.id}: {error_msg}")
            return SMTPValidator._finalize_result(
                smtp_config, 
                False, 
                error_msg, 
                0
            )

    @staticmethod
    def _validate_required_fields(smtp_config):
        """
        Checks if mandatory fields are present.
        """
        if smtp_config.smtp_authentication:
            if not smtp_config.username:
                return "Usuário e senha obrigatórios para autenticação SMTP."
            if not smtp_config.password:
                return "Usuário e senha obrigatórios para autenticação SMTP."
        return None

    @staticmethod
    def _test_connection(smtp_config):
        """
        Attempts to open an SMTP connection.
        """
        connection = None
        try:
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
            return True, ""
        except socket.timeout:
            return False, "Timeout"
        except ssl.SSLError as e:
            return False, f"Erro SSL/TLS: {str(e)}"
        except (ConnectionError, socket.error) as e:
            return False, "Servidor indisponível"
        except Exception as e:
            err_str = str(e).lower()
            if "authentication failed" in err_str or "login failed" in err_str:
                return False, "Falha de autenticação"
            return False, f"Erro de conexão: {str(e)}"
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass

    @staticmethod
    def _finalize_result(smtp_config, success, message, response_time_ms, status_name=None):
        """
        Updates the model and returns the result.
        """
        smtp_config.last_validation_message = message
        smtp_config.last_error_message = "" if success else message
        smtp_config.last_response_time_ms = response_time_ms if success else 0
        
        if success:
            smtp_config.last_successful_connection_at = timezone.now()
            logger.info(f"SMTP {smtp_config.id} validado com sucesso.")
        else:
            logger.error(f"Erro SMTP {smtp_config.id}: {message}")

        if status_name:
            status_obj = ConnectionStatus.objects.filter(status__iexact=status_name).first()
            if status_obj:
                smtp_config.connection_status = status_obj

        smtp_config.save()

        return {
            "success": success,
            "message": message,
            "response_time_ms": response_time_ms
        }
