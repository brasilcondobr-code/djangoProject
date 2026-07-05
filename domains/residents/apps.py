from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ResidentsAppConfig(AppConfig):
    name = 'domains.residents'
    label = 'residents'
    verbose_name = _("04. Moradores")
