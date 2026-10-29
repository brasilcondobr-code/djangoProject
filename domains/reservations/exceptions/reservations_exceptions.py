class ReservationsException(Exception):
    """Base exception for Reservations domain."""
    pass


class RentalError(ReservationsException):
    """Erro de regra de negócio no módulo 01. Locações."""
    pass


class RentalValidationError(RentalError):
    """Dados inválidos informados para uma locação."""
    pass


class RentalCapacityError(RentalError):
    """Capacidade de agendamentos/reservas excedida ou não configurada."""
    pass


class RentalTransitionError(RentalError):
    """Transição de status não permitida para a locação."""
    pass


class MaintenanceReservationError(ReservationsException):
    """Erro de regra de negócio no módulo 02. Manutenções."""
    pass


class MaintenanceReservationValidationError(MaintenanceReservationError):
    """Dados inválidos informados para uma manutenção."""
    pass


class MaintenanceReservationTransitionError(MaintenanceReservationError):
    """Transição de status não permitida para a manutenção."""
    pass
