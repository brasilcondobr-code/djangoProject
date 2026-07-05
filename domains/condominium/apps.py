from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CondominiumAppConfig(AppConfig):
    name = 'domains.condominium'
    label = 'condominium'
    verbose_name = _('03. Condomínio')

