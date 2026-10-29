"""Validadores puros do módulo 02. Manutenções.

Não dependem do Admin nem de banco: recebem valores e levantam
:class:`MaintenanceReservationValidationError` com mensagens em português.
"""

from domains.reservations.exceptions import (
    MaintenanceReservationValidationError,
)

APPLICANT_MAX_LENGTH = 255


def normalize_applicant(value):
    """Remove espaços das bordas e exige solicitante não vazio."""
    applicant = (value or "").strip() if isinstance(value, str) else value
    if not applicant:
        raise MaintenanceReservationValidationError(
            "O solicitante é obrigatório."
        )
    if len(applicant) > APPLICANT_MAX_LENGTH:
        raise MaintenanceReservationValidationError(
            f"O solicitante deve ter no máximo {APPLICANT_MAX_LENGTH} caracteres."
        )
    return applicant


def normalize_observations(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value)
    return value.strip()


def validate_period(start_date, end_date):
    """Valida o intervalo inclusivo de datas."""
    if not start_date:
        raise MaintenanceReservationValidationError(
            "A data inicial é obrigatória."
        )
    if not end_date:
        raise MaintenanceReservationValidationError(
            "A data final é obrigatória."
        )
    if end_date < start_date:
        raise MaintenanceReservationValidationError(
            "A data final deve ser maior ou igual à data inicial."
        )
