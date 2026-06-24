from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AdministrativeAppConfig(AppConfig):
    name = 'domains.administrative'
    label = 'administrative'
    verbose_name = _('05. Administrativo')