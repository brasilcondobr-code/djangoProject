from django.db import transaction
import logging
from domains.administrative.models.circular import Circular
from domains.email_service.models import ShippingQueue, ConnectionStatus, SMTPConfiguration, UsageProfiles
from domains.residents.models import Resident

logger = logging.getLogger(__name__)

class CircularEmailQueueService:
    @staticmethod
    @transaction.atomic
    def queue_circular_emails(circular: Circular):
        """
        Queues emails for all residents associated with a circular.
        Returns a dict with the results of the operation.
        """
        results = {
            'queued': 0,
            'total_residents': 0,
            'no_email': 0,
            'already_queued': 0,
            'errors': 0
        }

        residents = circular.residents.all()
        results['total_residents'] = residents.count()
        
        if not residents.exists():
            return results

        # Get the SMTP configuration from the circular, or fallback to the first active one if none specified
        smtp_config = circular.email_smtp_configuration
        if not smtp_config:
            smtp_config = SMTPConfiguration.objects.filter(is_active=True).first()

        # Get a usage profile. In a real system, we might have one specifically for circulars.
        usage_profile = UsageProfiles.objects.filter(is_active=True).first()

        # Get the 'Pendente' connection status
        pending_status = ConnectionStatus.objects.filter(status__iexact='Pendente').first()
        if not pending_status:
            pass

        for resident in residents:
            try:
                if not resident.email:
                    results['no_email'] += 1
                    continue

                # Check if this email is already queued for this circular to avoid duplicates
                exists = ShippingQueue.objects.filter(
                    module_origin="administrative_circular",
                    reference_id=circular.id,
                    to_email=resident.email
                ).exists()

                if exists:
                    results['already_queued'] += 1
                    continue

                ShippingQueue.objects.create(
                    condominium=circular.condominium,
                    module_origin="administrative_circular",
                    reference_id=circular.id,
                    subject=f"[Circular] {circular.title}",
                    to_email=resident.email,
                    message=circular.circular_content,
                    html_message=circular.circular_content, # Assuming content can be HTML
                    smtp_configuration=smtp_config,
                    usage_profile=usage_profile,
                    status=pending_status,
                    is_active=True
                )
                results['queued'] += 1
            except Exception as e:
                logger.error(f"Error queuing email for resident {resident.id}: {str(e)}", extra={
                    "circular_id": circular.id,
                    "resident_id": resident.id
                })
                results['errors'] += 1
        
        return results
