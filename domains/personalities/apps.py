from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GatehouseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.personalities'
    verbose_name = _('02. Personalidades')
    