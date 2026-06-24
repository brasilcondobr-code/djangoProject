from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class GatehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.gatehouse'
    verbose_name = _('08. Portaria')