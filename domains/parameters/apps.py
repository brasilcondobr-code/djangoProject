from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ParametersAppConfig(AppConfig):
    name = 'domains.parameters'
    label = 'parameters'
    verbose_name = _('01. Parâmetros')

    def ready(self):
        # Registra o modelo somente após todos os apps carregarem seus
        # modelos. Isso evita que a FK para condominium.Condominium seja
        # resolvida antes do registro definitivo daquele modelo.
        from .models.fund_financial import FundFinancial  # noqa: F401
