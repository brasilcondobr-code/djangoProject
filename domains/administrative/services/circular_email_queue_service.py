from django.db import transaction
import logging
from domains.email_service.models import ShippingQueue, ConnectionStatus, SMTPConfiguration, UsageProfiles, TypesPriority
 
logger = logging.getLogger(__name__)
 
class AdministrativeEmailQueueService:

    @staticmethod
    @transaction.atomic
    def queue_emails(entity, residents, module_origin, subject, message, smtp_config_field, attachment=None):
        """
        Generic method to queue emails for any administrative entity.
        """
        results = {
            'queued': 0,
            'total_residents': 0,
            'no_email': 0,
            'already_queued': 0,
            'errors': 0
        }

        results['total_residents'] = residents.count()
        
        if not residents.exists():
            return results

        # Get the SMTP configuration from the entity, or fallback to the first active one if none specified
        smtp_config = getattr(entity, smtp_config_field, None)
        if not smtp_config:
            smtp_config = SMTPConfiguration.objects.filter(is_active=True).first()

        # Get a usage profile.
        usage_profile = UsageProfiles.objects.filter(is_active=True).first()

        # Get the 'Pendente' connection status
        pending_status = ConnectionStatus.objects.filter(status__iexact='Pendente').first()

        # Get the 'Normal' priority
        normal_priority = TypesPriority.objects.filter(priority__iexact='Normal').first()
 
        for resident in residents:

            try:
                if not resident.email:
                    results['no_email'] += 1
                    continue

                # Extract Condominium object.
                # Handle both ManyToManyField (returns manager) and ForeignKey (returns instance)
                condominium_val = getattr(entity, 'condominium', None)
                condominium_obj = None
                
                if condominium_val:
                    if hasattr(condominium_val, 'all'): # It's a manager (ManyToManyField)
                        first_unit = condominium_val.first()
                        if first_unit:
                            condominium_obj = getattr(first_unit, 'condominium', None)
                    elif hasattr(condominium_val, 'condominium'): # It's a CondominiumUnit instance
                        condominium_obj = condominium_val.condominium
                    else: # It might already be a Condominium instance
                        condominium_obj = condominium_val

                # Check if this email is already queued and active to avoid duplicates
                # We only block if it is ACTIVE and NOT yet sent.
                # If it was already sent or is inactive, we allow creating a new entry for a new attempt.
                exists = ShippingQueue.objects.filter(
                    module_origin=module_origin,
                    reference_id=entity.id,
                    to_email=resident.email,
                    is_active=True,
                    sent_at__isnull=True
                ).exists()
 
                if exists:
                    results['already_queued'] += 1
                    continue
 
                try:
                    ShippingQueue.objects.create(
                        condominium=condominium_obj,
                        module_origin=module_origin,
                        reference_id=entity.id,
                        subject=subject,
                        to_email=resident.email,
                        message=message,
                        html_message=message, 
                        smtp_configuration=smtp_config,
                        usage_profile=usage_profile,
                        status=pending_status,
                        priority=normal_priority,
                        is_active=True,
                        attachments=attachment
                    )
                    results['queued'] += 1
                except Exception:
                    # Fallback: If create fails (e.g. UniqueConstraint), we reset the existing record
                    queue_item = ShippingQueue.objects.filter(
                        module_origin=module_origin,
                        reference_id=entity.id,
                        to_email=resident.email
                    ).first()
                    if queue_item:
                        queue_item.is_active = True
                        queue_item.sent_at = None
                        queue_item.status = pending_status
                        queue_item.subject = subject
                        queue_item.message = message
                        queue_item.html_message = message
                        queue_item.smtp_configuration = smtp_config
                        queue_item.usage_profile = usage_profile
                        queue_item.attachments = attachment
                        queue_item.save()
                        results['queued'] += 1
                    else:
                        results['errors'] += 1

            except Exception as e:
                logger.error(f"Error queuing email for entity {entity.id} and resident {resident.id}: {str(e)}", extra={
                    "entity_id": entity.id,
                    "resident_id": resident.id
                })
                results['errors'] += 1
        
        return results
