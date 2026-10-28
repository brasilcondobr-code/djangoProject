"""Validadores puros do módulo 01. Locações.

Não dependem do Admin nem de banco: recebem valores e levantam
:class:`RentalValidationError` com mensagens em português.
"""

from decimal import Decimal, InvalidOperation

from domains.reservations.exceptions import RentalValidationError

APPLICANT_MAX_LENGTH = 255
RENTAL_PRICE_MAX_DIGITS = 14
RENTAL_PRICE_DECIMAL_PLACES = 2


def normalize_applicant(value):
    """Remove espaços das bordas e exige solicitante não vazio."""
    applicant = (value or "").strip() if isinstance(value, str) else value
    if not applicant:
        raise RentalValidationError("O solicitante é obrigatório.")
    if len(applicant) > APPLICANT_MAX_LENGTH:
        raise RentalValidationError(
            f"O solicitante deve ter no máximo {APPLICANT_MAX_LENGTH} caracteres."
        )
    return applicant


def normalize_observations(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value)
    return value.strip()


def parse_rental_price(value):
    """Converte o valor recebido (inclusive no formato pt-BR) em Decimal."""
    if value in (None, ""):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))

    text = str(value).strip().replace(" ", "")
    if not text:
        return None
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")

    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        raise RentalValidationError("O valor da locação é inválido.")


def validate_period(start_date, end_date):
    """Valida o intervalo inclusivo de datas."""
    if not start_date:
        raise RentalValidationError("A data inicial é obrigatória.")
    if not end_date:
        raise RentalValidationError("A data final é obrigatória.")
    if end_date < start_date:
        raise RentalValidationError(
            "A data final deve ser maior ou igual à data inicial."
        )


def validate_price(charge_amount, rental_price):
    """Normaliza o preço conforme a cobrança.

    Com cobrança (``charge_amount=True``) o valor é obrigatório e maior que
    zero. Sem cobrança o valor é limpo para ``None`` (decisão aprovada), para
    não persistir preço enganoso.
    """
    if not charge_amount:
        return None

    price = parse_rental_price(rental_price)
    if price is None:
        raise RentalValidationError(
            "Informe o valor da locação quando a cobrança estiver habilitada."
        )
    if price <= 0:
        raise RentalValidationError(
            "O valor da locação deve ser maior que zero."
        )

    try:
        quantized = price.quantize(Decimal("0.01"))
    except InvalidOperation:
        raise RentalValidationError(
            f"O valor da locação deve ter no máximo {RENTAL_PRICE_MAX_DIGITS} "
            "dígitos, incluindo as casas decimais."
        )
    integer_digits = len(quantized.as_tuple().digits) - RENTAL_PRICE_DECIMAL_PLACES
    if integer_digits > (RENTAL_PRICE_MAX_DIGITS - RENTAL_PRICE_DECIMAL_PLACES):
        raise RentalValidationError(
            f"O valor da locação deve ter no máximo {RENTAL_PRICE_MAX_DIGITS} "
            "dígitos, incluindo as casas decimais."
        )
    return quantized
