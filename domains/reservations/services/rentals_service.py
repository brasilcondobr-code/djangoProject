"""Regras de negócio do módulo 01. Locações.

Centraliza validação de período/preço, controle de capacidade por
sobreposição e transições de status. A camada Admin apenas delega para cá.

Concorrência: as verificações de capacidade bloqueiam a linha do
``TypesOfRental`` (``select_for_update``) e as edições/transições bloqueiam a
linha da própria locação. O Admin executa o POST dentro de
``transaction.atomic`` (``ModelAdmin.changeform_view``), portanto o lock é
mantido até o commit. Fora de uma transação ativa (ex.: testes de formulário),
o lock é dispensado — o SQLite usado nos testes também o ignora.
"""

import logging

from django.db import connection, transaction

from domains.parameters.models import TypesOfRental
from domains.reservations.exceptions import (
    RentalCapacityError,
    RentalError,
    RentalTransitionError,
    RentalValidationError,
)
from domains.reservations.models import Rentals
from domains.reservations.repositories import ReservationsRepository
from domains.reservations.selectors import ReservationsSelector
from domains.reservations.validators import (
    normalize_applicant,
    normalize_observations,
    validate_period,
    validate_price,
)

logger = logging.getLogger(__name__)

EDITABLE_FIELDS = (
    "condominium",
    "typesOfRentals",
    "startDate",
    "endDate",
    "applicant",
    "rentalPrice",
    "charge_amount",
    "observations",
    "is_active",
)

# status -> (campo de limite, singular, plural)
LIMIT_CONFIG = {
    Rentals.Status.AGENDAMENTO: (
        "numberOfAppointments",
        "agendamento",
        "agendamentos",
    ),
    Rentals.Status.RESERVADO: (
        "numberOfReservations",
        "reserva",
        "reservas",
    ),
}


def _authenticated(user):
    return bool(user and getattr(user, "is_authenticated", False))


def _coerce_bool(value, default=True):
    """Normaliza booleanos vindos de formulários, strings ou ausentes."""
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "sim", "yes", "on")
    return bool(value)


class RentalsService:

    # ------------------------------------------------------------------
    # Validações
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_instance(instance):
        if instance is None:
            raise RentalValidationError("Locação não encontrada.")

        instance.applicant = normalize_applicant(instance.applicant)
        instance.observations = normalize_observations(instance.observations)
        validate_period(instance.startDate, instance.endDate)
        instance.rentalPrice = validate_price(
            instance.charge_amount, instance.rentalPrice
        )

        if not instance.condominium_id:
            raise RentalValidationError("A unidade é obrigatória.")
        if not instance.typesOfRentals_id:
            raise RentalValidationError(
                "O tipo de locação é obrigatório."
            )
        return instance

    @staticmethod
    def _locked_rental_type(rental, limit_field):
        """Obtém o tipo de locação, com lock quando há transação ativa."""
        queryset = TypesOfRental.objects
        if connection.in_atomic_block:
            queryset = queryset.select_for_update()
        return (
            queryset.filter(pk=rental.typesOfRentals_id)
            .only("pk", "description", limit_field)
            .first()
        )

    @staticmethod
    def _assert_capacity(rental, *, status, exclude_self):
        """Valida o limite do status informado no escopo da locação.

        Deve ser chamado dentro de ``transaction.atomic`` para que o lock do
        tipo de locação proteja a contagem até a gravação.
        """
        config = LIMIT_CONFIG.get(status)
        if config is None:
            return
        limit_field, _singular, plural = config

        rental_type = RentalsService._locked_rental_type(rental, limit_field)
        if rental_type is None:
            raise RentalValidationError("Tipo de locação não encontrado.")

        limit = getattr(rental_type, limit_field)
        if limit is None:
            raise RentalCapacityError(
                f"O tipo de locação '{rental_type.description}' não possui "
                f"limite de {plural} configurado. Ajuste o cadastro do tipo "
                "de locação antes de continuar."
            )
        if limit <= 0:
            raise RentalCapacityError(
                f"O tipo de locação '{rental_type.description}' está "
                f"configurado com limite {limit} de {plural}; nenhum registro "
                "é permitido."
            )

        overlapping = ReservationsSelector.count_overlapping_rentals(
            unit_id=rental.condominium_id,
            rental_type_id=rental.typesOfRentals_id,
            status=status,
            start_date=rental.startDate,
            end_date=rental.endDate,
            exclude_pk=rental.pk if exclude_self else None,
        )
        if overlapping >= limit:
            label = plural if limit != 1 else _singular
            raise RentalCapacityError(
                f"Limite de {limit} {label} atingido para o tipo "
                f"'{rental_type.description}' no período informado."
            )

    @staticmethod
    def assert_capacity_for_form(instance):
        """Checagem usada pelo formulário (erro amigável no próprio campo)."""
        if not (
            instance.condominium_id
            and instance.typesOfRentals_id
            and instance.startDate
            and instance.endDate
        ):
            return
        RentalsService._assert_capacity(
            instance,
            status=Rentals.Status.AGENDAMENTO,
            exclude_self=bool(instance.pk),
        )

    # ------------------------------------------------------------------
    # Criação / edição
    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def save_instance(instance, user=None, is_new=False, check_capacity=True):
        """Persiste uma instância já preenchida (Admin ou uso programático).

        Em edição, bloqueia a linha original e garante que somente locações
        em Agendamento sejam alteradas. ``created_by`` nunca é sobrescrito.
        """
        if instance is None:
            raise RentalValidationError("Locação não encontrada.")

        if is_new:
            instance.pk = None
            instance.status = Rentals.Status.AGENDAMENTO
            instance.errorStatus = ""
            instance.created_by = user if _authenticated(user) else None
            instance.updated_by = instance.created_by
        else:
            try:
                locked = ReservationsRepository.get_rental_for_update(
                    instance.pk
                )
            except Rentals.DoesNotExist:
                raise RentalValidationError("Locação não encontrada.")

            if locked.status != Rentals.Status.AGENDAMENTO:
                raise RentalTransitionError(
                    "Somente locações em Agendamento podem ser editadas. "
                    f"Status atual: '{locked.get_status_display()}'."
                )
            instance.status = locked.status
            instance.created_by_id = locked.created_by_id
            instance.updated_by = user if _authenticated(user) else None
            instance.errorStatus = ""

        RentalsService._validate_instance(instance)

        if check_capacity:
            RentalsService._assert_capacity(
                instance,
                status=Rentals.Status.AGENDAMENTO,
                exclude_self=not is_new,
            )

        if is_new:
            ReservationsRepository.create_rental(instance)
        else:
            ReservationsRepository.update_rental(instance)

        logger.info(
            "rental_saved",
            extra={
                "rental_id": instance.pk,
                "unit_id": instance.condominium_id,
                "rental_type_id": instance.typesOfRentals_id,
                "status": instance.status,
                "operation": "create" if is_new else "update",
                "user_id": getattr(user, "pk", None),
            },
        )
        return instance

    @staticmethod
    @transaction.atomic
    def create_rental(data, user=None):
        instance = Rentals(
            condominium=data.get("condominium"),
            typesOfRentals=data.get("typesOfRentals"),
            startDate=data.get("startDate"),
            endDate=data.get("endDate"),
            applicant=data.get("applicant"),
            rentalPrice=data.get("rentalPrice"),
            charge_amount=_coerce_bool(data.get("charge_amount"), True),
            observations=data.get("observations") or "",
            is_active=_coerce_bool(data.get("is_active"), True),
        )
        return RentalsService.save_instance(
            instance, user=user, is_new=True, check_capacity=True
        )

    @staticmethod
    @transaction.atomic
    def update_rental(instance, data, user=None):
        if instance is None:
            raise RentalValidationError("Locação não encontrada.")
        for field in EDITABLE_FIELDS:
            if field in data:
                setattr(instance, field, data[field])
        return RentalsService.save_instance(
            instance, user=user, is_new=False, check_capacity=True
        )

    # ------------------------------------------------------------------
    # Transições em lote
    # ------------------------------------------------------------------
    @staticmethod
    def reserve_rentals(rental_ids, user=None):
        return RentalsService._transition_batch(
            rental_ids,
            user=user,
            from_status=Rentals.Status.AGENDAMENTO,
            to_status=Rentals.Status.RESERVADO,
            capacity_status=Rentals.Status.RESERVADO,
        )

    @staticmethod
    def finalize_rentals(rental_ids, user=None):
        return RentalsService._transition_batch(
            rental_ids,
            user=user,
            from_status=Rentals.Status.RESERVADO,
            to_status=Rentals.Status.FINALIZADO,
            capacity_status=None,
        )

    @staticmethod
    def _transition_batch(
        rental_ids,
        *,
        user,
        from_status,
        to_status,
        capacity_status,
    ):
        """Processa cada locação isoladamente, permitindo sucesso parcial.

        O ``errorStatus`` é gravado fora do savepoint que falhou, para não ser
        desfeito pelo rollback daquele registro.
        """
        results = []
        for rental_id in rental_ids:
            try:
                with transaction.atomic():
                    rental = ReservationsRepository.get_rental_for_update(
                        rental_id
                    )
                    if not rental.is_active:
                        raise RentalTransitionError(
                            "Locação inativa não pode ser "
                            f"{to_status.label.lower()}."
                        )
                    if rental.status != from_status:
                        raise RentalTransitionError(
                            f"Status atual '{rental.get_status_display()}' não "
                            f"permite {to_status.label.lower()}. É necessário "
                            f"estar em '{from_status.label}'."
                        )
                    if capacity_status is not None:
                        RentalsService._assert_capacity(
                            rental,
                            status=capacity_status,
                            exclude_self=True,
                        )

                    rental.status = to_status
                    rental.errorStatus = ""
                    if _authenticated(user):
                        rental.updated_by = user
                    rental.save(
                        update_fields=[
                            "status",
                            "errorStatus",
                            "updated_by",
                            "updated_at",
                        ]
                    )

                results.append(
                    {"pk": rental_id, "success": True, "message": ""}
                )
                logger.info(
                    "rental_status_changed",
                    extra={
                        "rental_id": rental_id,
                        "from_status": from_status,
                        "to_status": to_status,
                        "user_id": getattr(user, "pk", None),
                        "operation": "transition",
                    },
                )
            except Rentals.DoesNotExist:
                message = "Locação não encontrada."
                results.append(
                    {"pk": rental_id, "success": False, "message": message}
                )
                logger.warning(
                    "rental_transition_missing",
                    extra={"rental_id": rental_id, "to_status": to_status},
                )
            except RentalError as exc:
                message = str(exc)
                ReservationsRepository.set_error_status(rental_id, message)
                results.append(
                    {"pk": rental_id, "success": False, "message": message}
                )
                logger.warning(
                    "rental_transition_rejected",
                    extra={
                        "rental_id": rental_id,
                        "to_status": to_status,
                        "error": message,
                        "user_id": getattr(user, "pk", None),
                    },
                )
            except Exception:
                message = "Erro inesperado ao processar a locação."
                ReservationsRepository.set_error_status(rental_id, message)
                results.append(
                    {"pk": rental_id, "success": False, "message": message}
                )
                logger.exception(
                    "rental_transition_error",
                    extra={
                        "rental_id": rental_id,
                        "to_status": to_status,
                        "user_id": getattr(user, "pk", None),
                    },
                )
        return results
