from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FinancialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.financial'
    verbose_name = _('07. Financeiro')
