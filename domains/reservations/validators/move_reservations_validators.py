"""Validadores puros do módulo 03. Mudanças.

Não dependem do Admin nem de banco: recebem valores e levantam
:class:`MoveReservationValidationError` com mensagens em português.
"""

from domains.reservations.exceptions import MoveReservationValidationError

APPLICANT_MAX_LENGTH = 255

TYPE_ENTRADA = "E"
TYPE_SAIDA = "S"
VALID_TYPES_OF_CHANGE = {TYPE_ENTRADA, TYPE_SAIDA}


def normalize_applicant(value):
    """Remove espaços das bordas e exige solicitante não vazio."""
    applicant = (value or "").strip() if isinstance(value, str) else value
    if not applicant:
        raise MoveReservationValidationError("O solicitante é obrigatório.")
    if len(applicant) > APPLICANT_MAX_LENGTH:
        raise MoveReservationValidationError(
            f"O solicitante deve ter no máximo {APPLICANT_MAX_LENGTH} caracteres."
        )
    return applicant


def normalize_observations(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value)
    return value.strip()


def validate_type_of_change(value):
    if value not in VALID_TYPES_OF_CHANGE:
        raise MoveReservationValidationError(
            "Selecione o tipo de mudança (Entrada ou Saída)."
        )
    return value


def validate_period(start_date, end_date):
    """Valida o intervalo inclusivo de datas."""
    if not start_date:
        raise MoveReservationValidationError("A data inicial é obrigatória.")
    if not end_date:
        raise MoveReservationValidationError("A data final é obrigatória.")
    if end_date < start_date:
        raise MoveReservationValidationError(
            "A data final deve ser maior ou igual à data inicial."
        )
