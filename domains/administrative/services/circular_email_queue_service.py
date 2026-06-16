from django.db import transaction
from django.conf import settings
from domains.administrative.models.circular import Circular
from domains.email_service.models import ShippingQueue, ConnectionStatus, SMTPConfiguration, UsageProfiles
from domains.residents.models import Resident

class CircularEmailQueueService:
    @staticmethod
    @transaction.atomic
    def queue_circular_emails(circular: Circular):
        """
        Queues emails for all residents associated with a circular.
        """
        residents = circular.residents.all()
        if not residents.exists():
            return 0

        # Get the SMTP configuration from the circular, or fallback to the first active one if none specified
        smtp_config = circular.email_smtp_configuration
        if not smtp_config:
            smtp_config = SMTPConfiguration.objects.filter(is_active=True).first()

        # Get a usage profile. In a real system, we might have one specifically for circulars.
        # For now, we try to find one or skip if none found.
        usage_profile = UsageProfiles.objects.filter(is_active=True).first()

        # Get the 'Pendente' connection status
        # Assuming 'Pendente' exists. If not, we might need to create it or use another.
        # Based on previous work, we've been ensuring certain statuses exist.
        pending_status = ConnectionStatus.objects.filter(status__iexact='Pendente').first()
        if not pending_status:
            # Fallback: try to get any status if 'Pendente' is missing, or just leave it null.
            # Better yet, let's assume it exists as part of the system setup.
            pass

        count = 0
        for resident in residents:
            if not resident.email:
                continue

            # Check if this email is already queued for this circular to avoid duplicates
            # The ShippingQueue has a unique constraint on (module_origin, reference_id, to_email)
            exists = ShippingQueue.objects.filter(
                module_origin="administrative_circular",
                reference_id=circular.id,
                to_email=resident.email
            ).exists()

            if exists:
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
            count += 1
        
        return count
