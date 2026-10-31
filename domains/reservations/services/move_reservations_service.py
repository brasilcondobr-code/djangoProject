"""Regras de negócio do módulo 03. Mudanças.

Centraliza validação de período/tipo, bloqueio de edição por status e
transições ``Agendamento -> Execução -> Finalizado``. A camada Admin apenas
delega para cá.

Concorrência: edições e transições bloqueiam a linha da própria mudança
dentro de uma transação. O Admin executa o POST em ``transaction.atomic``
(``ModelAdmin.changeform_view``), portanto o lock é mantido até o commit.
Fora de uma transação ativa o lock é dispensado (o SQLite dos testes também o
ignora).
"""

import logging

from django.db import transaction

from domains.reservations.exceptions import (
    MoveReservationError,
    MoveReservationTransitionError,
    MoveReservationValidationError,
)
from domains.reservations.models import MoveReservations
from domains.reservations.repositories import ReservationsRepository
from domains.reservations.validators.move_reservations_validators import (
    normalize_applicant,
    normalize_observations,
    validate_period,
    validate_type_of_change,
)

logger = logging.getLogger(__name__)

EDITABLE_FIELDS = (
    "condominium",
    "typeOfChange",
    "startDate",
    "endDate",
    "applicant",
    "observations",
    "is_active",
)


def _authenticated(user):
    return bool(user and getattr(user, "is_authenticated", False))


def _coerce_bool(value, default=True):
    """Normaliza booleanos vindos de formulários, strings ou ausentes."""
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "sim", "yes", "on")
    return bool(value)


class MoveReservationsService:

    # ------------------------------------------------------------------
    # Validações
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_instance(instance):
        if instance is None:
            raise MoveReservationValidationError("Mudança não encontrada.")

        instance.applicant = normalize_applicant(instance.applicant)
        instance.observations = normalize_observations(instance.observations)
        instance.typeOfChange = validate_type_of_change(instance.typeOfChange)
        validate_period(instance.startDate, instance.endDate)

        if not instance.condominium_id:
            raise MoveReservationValidationError("A unidade é obrigatória.")
        return instance

    # ------------------------------------------------------------------
    # Criação / edição
    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def save_instance(instance, user=None, is_new=False):
        """Persiste uma instância já preenchida (Admin ou uso programático).

        Em edição, bloqueia a linha original e garante que somente mudanças em
        Agendamento sejam alteradas. ``created_by`` nunca é sobrescrito e
        ``status`` nunca vem do cliente.
        """
        if instance is None:
            raise MoveReservationValidationError("Mudança não encontrada.")

        if is_new:
            instance.pk = None
            instance.status = MoveReservations.Status.AGENDAMENTO
            instance.created_by = user if _authenticated(user) else None
            instance.updated_by = instance.created_by
        else:
            try:
                locked = (
                    ReservationsRepository.get_move_reservation_for_update(
                        instance.pk
                    )
                )
            except MoveReservations.DoesNotExist:
                raise MoveReservationValidationError("Mudança não encontrada.")

            if locked.status != MoveReservations.Status.AGENDAMENTO:
                raise MoveReservationTransitionError(
                    "Somente mudanças em Agendamento podem ser editadas. "
                    f"Status atual: '{locked.get_status_display()}'."
                )
            instance.status = locked.status
            instance.created_by_id = locked.created_by_id
            instance.updated_by = user if _authenticated(user) else None

        MoveReservationsService._validate_instance(instance)

        if is_new:
            ReservationsRepository.create_move_reservation(instance)
        else:
            ReservationsRepository.update_move_reservation(instance)

        logger.info(
            "move_reservation_saved",
            extra={
                "move_id": instance.pk,
                "unit_id": instance.condominium_id,
                "type_of_change": instance.typeOfChange,
                "status": instance.status,
                "operation": "create" if is_new else "update",
                "user_id": getattr(user, "pk", None),
            },
        )
        return instance

    @staticmethod
    @transaction.atomic
    def create_move(data, user=None):
        instance = MoveReservations(
            condominium=data.get("condominium"),
            typeOfChange=data.get("typeOfChange"),
            startDate=data.get("startDate"),
            endDate=data.get("endDate"),
            applicant=data.get("applicant"),
            observations=data.get("observations") or "",
            is_active=_coerce_bool(data.get("is_active"), True),
        )
        return MoveReservationsService.save_instance(
            instance, user=user, is_new=True
        )

    @staticmethod
    @transaction.atomic
    def update_move(instance, data, user=None):
        if instance is None:
            raise MoveReservationValidationError("Mudança não encontrada.")
        for field in EDITABLE_FIELDS:
            if field in data:
                setattr(instance, field, data[field])
        return MoveReservationsService.save_instance(
            instance, user=user, is_new=False
        )

    # ------------------------------------------------------------------
    # Transições em lote
    # ------------------------------------------------------------------
    @staticmethod
    def execute_moves(move_ids, user=None):
        return MoveReservationsService._transition_batch(
            move_ids,
            user=user,
            from_status=MoveReservations.Status.AGENDAMENTO,
            to_status=MoveReservations.Status.EXECUCAO,
        )

    @staticmethod
    def finalize_moves(move_ids, user=None):
        return MoveReservationsService._transition_batch(
            move_ids,
            user=user,
            from_status=MoveReservations.Status.EXECUCAO,
            to_status=MoveReservations.Status.FINALIZADO,
        )

    @staticmethod
    def _transition_batch(move_ids, *, user, from_status, to_status):
        """Processa cada mudança isoladamente, permitindo sucesso parcial.

        Cada item usa seu próprio ``transaction.atomic`` (savepoint), para que
        a falha de um registro não desfaça os demais. Nenhuma mensagem de erro
        é persistida no banco: o resultado é apenas reportado ao Admin.
        """
        results = []
        for move_id in move_ids:
            try:
                with transaction.atomic():
                    move = (
                        ReservationsRepository.get_move_reservation_for_update(
                            move_id
                        )
                    )
                    if move.status != from_status:
                        raise MoveReservationTransitionError(
                            f"Status atual '{move.get_status_display()}' "
                            f"não permite {to_status.label.lower()}. É "
                            f"necessário estar em '{from_status.label}'."
                        )

                    move.status = to_status
                    if _authenticated(user):
                        move.updated_by = user
                    move.save(
                        update_fields=[
                            "status",
                            "updated_by",
                            "updated_at",
                        ]
                    )

                results.append(
                    {"pk": move_id, "success": True, "message": ""}
                )
                logger.info(
                    "move_reservation_status_changed",
                    extra={
                        "move_id": move_id,
                        "from_status": from_status,
                        "to_status": to_status,
                        "user_id": getattr(user, "pk", None),
                        "operation": "transition",
                    },
                )
            except MoveReservations.DoesNotExist:
                message = "Mudança não encontrada."
                results.append(
                    {"pk": move_id, "success": False, "message": message}
                )
                logger.warning(
                    "move_reservation_transition_missing",
                    extra={"move_id": move_id, "to_status": to_status},
                )
            except MoveReservationError as exc:
                message = str(exc)
                results.append(
                    {"pk": move_id, "success": False, "message": message}
                )
                logger.warning(
                    "move_reservation_transition_rejected",
                    extra={
                        "move_id": move_id,
                        "to_status": to_status,
                        "error": message,
                        "user_id": getattr(user, "pk", None),
                    },
                )
            except Exception:
                message = "Erro inesperado ao processar a mudança."
                results.append(
                    {"pk": move_id, "success": False, "message": message}
                )
                logger.exception(
                    "move_reservation_transition_error",
                    extra={
                        "move_id": move_id,
                        "to_status": to_status,
                        "user_id": getattr(user, "pk", None),
                    },
                )
        return results
