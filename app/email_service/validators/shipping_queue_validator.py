from django.core.exceptions import ValidationError
from email_service.models import ShippingQueue, ConnectionStatus

class ShippingQueueValidator:
    @staticmethod
    def validate_for_sending(queue_item):
        """
        Valida se um item da fila pode ser enviado.
        """
        # 1. Validar se está ativo
        if not queue_item.is_active:
            raise ValidationError("O item da fila está inativo.")

        # 2. Validar status (deve ser Pendente ou Retentativa)
        # Nota: Usamos busca por string para ser resiliente a variações de tradução, 
        # mas o ideal é usar constantes ou IDs fixos se possível.
        status_name = queue_item.status.status.lower() if queue_item.status else ""
        
        if status_name not in ['pendente', 'retentativa', 'retry', 'pending']:
            raise ValidationError(f"O item não está em um estado que permite envio (Status atual: {queue_item.status}).")

        # 3. Validar limites de retry
        if queue_item.retry_count >= queue_item.max_retry_attempts:
            raise ValidationError("Limite máximo de tentativas atingido.")

        # 4. Validar campos obrigatórios do ShippingQueue
        if not queue_item.to_email:
            raise ValidationError("O destinatário é obrigatório.")
        if not queue_item.subject:
            raise ValidationError("O assunto é obrigatório.")
        if not queue_item.message:
            raise ValidationError("A mensagem é obrigatória.")
        if not queue_item.smtp_configuration:
            raise ValidationError("A configuração SMTP é obrigatória.")

        # 5. Validar campos da SMTPConfiguration
        smtp = queue_item.smtp_configuration
        if not smtp.is_active:
            raise ValidationError("A configuração SMTP selecionada está inativa.")
        if not smtp.smtp_host:
            raise ValidationError("O host SMTP é obrigatório.")
        if not smtp.smtp_port:
            raise ValidationError("A porta SMTP é obrigatória.")
            
        if smtp.smtp_authentication:
            if not smtp.username:
                raise ValidationError("Usuário e senha são obrigatórios para autenticação SMTP.")
            if not smtp.password:
                raise ValidationError("Usuário e senha são obrigatórios para autenticação SMTP.")

        return True
