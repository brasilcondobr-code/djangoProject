class GatehouseException(Exception):
    """Base exception for Gatehouse domain."""
    pass


class ServiceTransitionError(GatehouseException):
    """Erro de regra de negócio no módulo 02. Passagens de Serviços."""
    pass
