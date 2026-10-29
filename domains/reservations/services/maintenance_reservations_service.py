"""Regras de negócio do módulo 02. Manutenções.

Centraliza validação de período, bloqueio de edição por status e transições
``Agendamento -> Execução -> Finalizado``. A camada Admin apenas delega para
cá.

Concorrência: edições e transições bloqueiam a linha da própria manutenção
dentro de uma transação. O Admin executa o POST em ``transaction.atomic``
(``ModelAdmin.changeform_view``), portanto o lock é mantido até o commit.
Fora de uma transação ativa o lock é dispensado (o SQLite dos testes também o
ignora).
"""

import logging

from django.db import transaction

from domains.reservations.exceptions import (
    MaintenanceReservationError,
    MaintenanceReservationTransitionError,
    MaintenanceReservationValidationError,
)
from domains.reservations.models import MaintenanceReservations
from domains.reservations.repositories import ReservationsRepository
from domains.reservations.validators.maintenance_reservations_validators import (
    normalize_applicant,
    normalize_observations,
    validate_period,
)

logger = logging.getLogger(__name__)

EDITABLE_FIELDS = (
    "condominium",
    "typesOfMaintenance",
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


class MaintenanceReservationsService:

    # ------------------------------------------------------------------
    # Validações
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_instance(instance):
        if instance is None:
            raise MaintenanceReservationValidationError(
                "Manutenção não encontrada."
            )

        instance.applicant = normalize_applicant(instance.applicant)
        instance.observations = normalize_observations(instance.observations)
        validate_period(instance.startDate, instance.endDate)

        if not instance.condominium_id:
            raise MaintenanceReservationValidationError(
                "A unidade é obrigatória."
            )
        if not instance.typesOfMaintenance_id:
            raise MaintenanceReservationValidationError(
                "O tipo de manutenção é obrigatório."
            )
        return instance

    # ------------------------------------------------------------------
    # Criação / edição
    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def save_instance(instance, user=None, is_new=False):
        """Persiste uma instância já preenchida (Admin ou uso programático).

        Em edição, bloqueia a linha original e garante que somente manutenções
        em Agendamento sejam alteradas. ``created_by`` nunca é sobrescrito e
        ``status`` nunca vem do cliente.
        """
        if instance is None:
            raise MaintenanceReservationValidationError(
                "Manutenção não encontrada."
            )

        if is_new:
            instance.pk = None
            instance.status = MaintenanceReservations.Status.AGENDAMENTO
            instance.created_by = user if _authenticated(user) else None
            instance.updated_by = instance.created_by
        else:
            try:
                locked = (
                    ReservationsRepository.get_maintenance_reservation_for_update(
                        instance.pk
                    )
                )
            except MaintenanceReservations.DoesNotExist:
                raise MaintenanceReservationValidationError(
                    "Manutenção não encontrada."
                )

            if locked.status != MaintenanceReservations.Status.AGENDAMENTO:
                raise MaintenanceReservationTransitionError(
                    "Somente manutenções em Agendamento podem ser editadas. "
                    f"Status atual: '{locked.get_status_display()}'."
                )
            instance.status = locked.status
            instance.created_by_id = locked.created_by_id
            instance.updated_by = user if _authenticated(user) else None

        MaintenanceReservationsService._validate_instance(instance)

        if is_new:
            ReservationsRepository.create_maintenance_reservation(instance)
        else:
            ReservationsRepository.update_maintenance_reservation(instance)

        logger.info(
            "maintenance_reservation_saved",
            extra={
                "maintenance_id": instance.pk,
                "unit_id": instance.condominium_id,
                "maintenance_type_id": instance.typesOfMaintenance_id,
                "status": instance.status,
                "operation": "create" if is_new else "update",
                "user_id": getattr(user, "pk", None),
            },
        )
        return instance

    @staticmethod
    @transaction.atomic
    def create_maintenance(data, user=None):
        instance = MaintenanceReservations(
            condominium=data.get("condominium"),
            typesOfMaintenance=data.get("typesOfMaintenance"),
            startDate=data.get("startDate"),
            endDate=data.get("endDate"),
            applicant=data.get("applicant"),
            observations=data.get("observations") or "",
            is_active=_coerce_bool(data.get("is_active"), True),
        )
        return MaintenanceReservationsService.save_instance(
            instance, user=user, is_new=True
        )

    @staticmethod
    @transaction.atomic
    def update_maintenance(instance, data, user=None):
        if instance is None:
            raise MaintenanceReservationValidationError(
                "Manutenção não encontrada."
            )
        for field in EDITABLE_FIELDS:
            if field in data:
                setattr(instance, field, data[field])
        return MaintenanceReservationsService.save_instance(
            instance, user=user, is_new=False
        )

    # ------------------------------------------------------------------
    # Transições em lote
    # ------------------------------------------------------------------
    @staticmethod
    def execute_maintenances(maintenance_ids, user=None):
        return MaintenanceReservationsService._transition_batch(
            maintenance_ids,
            user=user,
            from_status=MaintenanceReservations.Status.AGENDAMENTO,
            to_status=MaintenanceReservations.Status.EXECUCAO,
        )

    @staticmethod
    def finalize_maintenances(maintenance_ids, user=None):
        return MaintenanceReservationsService._transition_batch(
            maintenance_ids,
            user=user,
            from_status=MaintenanceReservations.Status.EXECUCAO,
            to_status=MaintenanceReservations.Status.FINALIZADO,
        )

    @staticmethod
    def _transition_batch(maintenance_ids, *, user, from_status, to_status):
        """Processa cada manutenção isoladamente, permitindo sucesso parcial.

        Cada item usa seu próprio ``transaction.atomic`` (savepoint), para que
        a falha de um registro não desfaça os demais. Nenhuma mensagem de erro
        é persistida no banco: o resultado é apenas reportado ao Admin.
        """
        results = []
        for maintenance_id in maintenance_ids:
            try:
                with transaction.atomic():
                    maintenance = (
                        ReservationsRepository.get_maintenance_reservation_for_update(
                            maintenance_id
                        )
                    )
                    if maintenance.status != from_status:
                        raise MaintenanceReservationTransitionError(
                            f"Status atual '{maintenance.get_status_display()}' "
                            f"não permite {to_status.label.lower()}. É "
                            f"necessário estar em '{from_status.label}'."
                        )

                    maintenance.status = to_status
                    if _authenticated(user):
                        maintenance.updated_by = user
                    maintenance.save(
                        update_fields=[
                            "status",
                            "updated_by",
                            "updated_at",
                        ]
                    )

                results.append(
                    {"pk": maintenance_id, "success": True, "message": ""}
                )
                logger.info(
                    "maintenance_reservation_status_changed",
                    extra={
                        "maintenance_id": maintenance_id,
                        "from_status": from_status,
                        "to_status": to_status,
                        "user_id": getattr(user, "pk", None),
                        "operation": "transition",
                    },
                )
            except MaintenanceReservations.DoesNotExist:
                message = "Manutenção não encontrada."
                results.append(
                    {"pk": maintenance_id, "success": False, "message": message}
                )
                logger.warning(
                    "maintenance_reservation_transition_missing",
                    extra={
                        "maintenance_id": maintenance_id,
                        "to_status": to_status,
                    },
                )
            except MaintenanceReservationError as exc:
                message = str(exc)
                results.append(
                    {"pk": maintenance_id, "success": False, "message": message}
                )
                logger.warning(
                    "maintenance_reservation_transition_rejected",
                    extra={
                        "maintenance_id": maintenance_id,
                        "to_status": to_status,
                        "error": message,
                        "user_id": getattr(user, "pk", None),
                    },
                )
            except Exception:
                message = "Erro inesperado ao processar a manutenção."
                results.append(
                    {"pk": maintenance_id, "success": False, "message": message}
                )
                logger.exception(
                    "maintenance_reservation_transition_error",
                    extra={
                        "maintenance_id": maintenance_id,
                        "to_status": to_status,
                        "user_id": getattr(user, "pk", None),
                    },
                )
        return results
