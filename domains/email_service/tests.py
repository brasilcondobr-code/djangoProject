import logging
from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from domains.email_service.models import (
    ShippingQueue,
    ConnectionStatus,
    SMTPConfiguration,
    TypesProvider,
    TypesPriority
)
from domains.email_service.services.queue_processor_service import QueueProcessorService


class QueueProcessorServiceTest(TestCase):
    def setUp(self):
        # 1. Setup Providers and Priorities
        self.provider = TypesProvider.objects.create(provider="SMTP")
        self.priority = TypesPriority.objects.create(priority="Normal")

        # 2. Setup Connection Statuses
        self.status_pendente = ConnectionStatus.objects.create(status="Pendente", description="Aguardando envio")
        self.status_enviado = ConnectionStatus.objects.create(status="Enviado", description="Enviado com sucesso")
        self.status_retentativa = ConnectionStatus.objects.create(status="Retentativa", description="Tentativa de reenvio")
        self.status_falha = ConnectionStatus.objects.create(status="Falha", description="Falha definitiva")

        # 3. Setup SMTP Configuration
        self.smtp_config = SMTPConfiguration.objects.create(
            description="Test SMTP",
            provider_code="test_smtp",
            provider_type=self.provider,
            smtp_host="localhost",
            smtp_port=1025,
            username="test@example.com",
            password="password",
            use_tls=False,
            use_ssl=False,
            api_supported=False
        )

        # 4. Setup Queue Item
        self.queue_item = ShippingQueue.objects.create(
            subject="Test Subject",
            to_email="recipient@example.com",
            smtp_configuration=self.smtp_config,
            status=self.status_pendente,
            priority=self.priority,
            is_active=True
        )

    @patch('domains.email_service.services.queue_processor_service.ProviderRouterService.route_and_send')
    def test_process_single_item_success(self, mock_route_and_send):
        # Arrange
        mock_route_and_send.return_value = {
            "success": True,
            "provider_response": {"provider": "localhost", "response_code": 250},
            "provider_message_id": "msg-id-123",
            "response_time_ms": 150,
            "logs": [{"event": "test_event", "message": "test message"}]
        }

        # Act
        result = QueueProcessorService.process_single_item(self.queue_item)

        # Assert
        self.assertTrue(result["success"])
        self.queue_item.refresh_from_db()
        self.assertEqual(self.queue_item.status, self.status_enviado)
        self.assertIsNotNone(self.queue_item.sent_at)
        self.assertEqual(self.queue_item.response_time_ms, 150)
        
        # Check logs (it's a JSONField, so it might be a dict or list depending on how it's stored/retrieved)
        # In the model it's default=dict. But QueueProcessorService appends to it.
        # If it's a dict, current_logs.append will fail if it's not a list.
        # Let's check how it's initialized in the model.
        # logs = models.JSONField(default=dict, ...)
        # In process_single_item: current_logs = item.logs if isinstance(item.logs, list) else []
        # So it handles it.
        
        logs_str = str(self.queue_item.logs)
        self.assertIn("test_event", logs_str)

    @patch('domains.email_service.services.queue_processor_service.ProviderRouterService.route_and_send')
    def test_process_single_item_failure_with_retry(self, mock_route_and_send):
        # Arrange
        mock_route_and_send.return_value = {
            "success": False,
            "provider_response": {},
            "provider_message_id": "",
            "response_time_ms": 50,
            "logs": [{"event": "error_event", "message": "smtp error"}],
            "error": "SMTP error"
        }

        # Act
        result = QueueProcessorService.process_single_item(self.queue_item)

        # Assert
        self.assertFalse(result["success"])
        self.queue_item.refresh_from_db()
        self.assertEqual(self.queue_item.status, self.status_retentativa)
        self.assertEqual(self.queue_item.retry_count, 1)
        self.assertIsNotNone(self.queue_item.next_retry_at)
        self.assertIn("SMTP error", self.queue_item.last_error_message)

    @patch('domains.email_service.services.queue_processor_service.ProviderRouterService.route_and_send')
    def test_process_single_item_failure_no_more_retries(self, mock_route_and_send):
        # Arrange
        self.queue_item.retry_count = 3 # Default max_retry_attempts is 3
        self.queue_item.save()

        mock_route_and_send.return_value = {
            "success": False,
            "provider_response": {},
            "provider_message_id": "",
            "response_time_ms": 50,
            "logs": [{"event": "error_event", "message": "permanent error"}],
            "error": "permanent error"
        }

        # Act
        result = QueueProcessorService.process_single_item(self.queue_item)

        # Assert
        self.assertFalse(result["success"])
        self.queue_item.refresh_from_db()
        self.assertEqual(self.queue_item.status, self.status_falha)
        self.assertFalse(self.queue_item.is_active)
