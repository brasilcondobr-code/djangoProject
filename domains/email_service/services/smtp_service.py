from domains.email_service.repositories.smtp_repository import SMTPRepository
from domains.email_service.models import SMTPConfiguration

class SMTPService:
    @staticmethod
    def set_default_configuration(configuration_id):
        configuration = SMTPConfiguration.objects.get(pk=configuration_id)
        SMTPRepository.set_as_default(configuration)
