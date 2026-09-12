"""
Registry de serviços de exportação (módulo 02. Exportações).

O campo `export_service` do ExportModule NÃO é código executável: é uma chave
que referencia um exportador previamente registrado no código-fonte. Isso
mantém o módulo extensível sem abrir risco de execução arbitrária.

  registry.resolve('parameters.condominium_types')  # -> exportador registrado
  registry.resolve('qualquer.coisa')                # -> ExportServiceNotFound
"""

from domains.data_management.exceptions import ExportServiceNotFound


class ExportServiceRegistry:
    """Mapa seguro de chave -> exportador, registrado somente em código."""

    def __init__(self):
        self._services = {}

    def register(self, service_key, exporter):
        """Registra um exportador para `service_key` (idempotente)."""
        if not service_key or not isinstance(service_key, str):
            raise ValueError('A chave do serviço de exportação é inválida.')
        self._services[service_key] = exporter
        return exporter

    def resolve(self, service_key):
        """Resolve um exportador registrado; rejeita chaves desconhecidas."""
        exporter = self._services.get(service_key)
        if exporter is None:
            raise ExportServiceNotFound(
                f'O serviço de exportação "{service_key}" não está registrado. '
                'Cadastre apenas chaves de serviços existentes no código.'
            )
        return exporter

    def registered(self):
        """Chaves registradas (ordem de registro)."""
        return tuple(self._services.keys())

    def is_registered(self, service_key):
        return service_key in self._services


# Instância global do módulo (singleton do processo).
registry = ExportServiceRegistry()

# Registra os exportadores padrão no import (evita registro duplicado e
# garante que o Admin/tasks encontrem os serviços mesmo sem import explícito).
from . import export_exporters  # noqa: E402,F401  (registra os serviços)