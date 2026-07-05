from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class EmailServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.email_service'
    verbose_name = _('06. E-mail')
