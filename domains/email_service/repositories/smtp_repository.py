from domains.email_service.models import SMTPConfiguration

class SMTPRepository:
    @staticmethod
    def get_active_configuration(configuration_id):
        return SMTPConfiguration.objects.get(
            id=configuration_id,
            is_active=True
        )

    @staticmethod
    def set_as_default(configuration):
        """
        Sets the given configuration as the default, 
        ensuring no other configuration is marked as default.
        """
        SMTPConfiguration.objects.filter(is_default=True).exclude(pk=configuration.pk).update(is_default=False)
        configuration.is_default = True
        configuration.save()
