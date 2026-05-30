from domains.email_service.models import SMTPConfiguration

class SMTPSelector:
    @staticmethod
    def get_active_configuration(configuration_id):
        return SMTPConfiguration.objects.get(
            id=configuration_id,
            is_active=True
        )
