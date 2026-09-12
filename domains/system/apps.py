from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.system'
    verbose_name = _('12. Sistema')

    def ready(self):
        from . import signals  # noqa: F401
