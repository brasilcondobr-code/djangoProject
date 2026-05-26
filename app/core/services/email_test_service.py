import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailTestService:

    @staticmethod
    def send_test_email(smtp_config):
        """
        Sends a test email using the provided SMTP configuration.
        """
        if not smtp_config.test_email_address:
            return False, "E-mail de teste não configurado."

        try:
            send_mail(
                subject='BrasilCondo - Teste SMTP',
                message='Teste automático do sistema.',
                from_email=smtp_config.username,
                recipient_list=[smtp_config.test_email_address],
                fail_silently=False,
            )
            return True, "E-mail de teste enviado com sucesso."
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de teste para {smtp_config.test_email_address}: {str(e)}")
            return False, f"Falha ao enviar e-mail de teste: {str(e)}"
