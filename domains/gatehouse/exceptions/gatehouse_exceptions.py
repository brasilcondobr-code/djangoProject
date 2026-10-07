class GatehouseException(Exception):
    """Base exception for Gatehouse domain."""
    pass


class ServiceTransitionError(GatehouseException):
    """Erro de regra de negócio no módulo 02. Passagens de Serviços."""
    pass


class UsefulPhoneNumberError(GatehouseException):
    """Erro de regra de negócio no módulo 03. Telefones Úteis."""
    pass


class OrderError(GatehouseException):
    """Erro de regra de negócio no módulo 04. Encomendas."""
    pass


class VisitorsRegisterError(GatehouseException):
    """Erro de regra de negócio no módulo 05. Reg. Visitantes."""
    pass
