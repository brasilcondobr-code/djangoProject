"""Service do módulo 05. Reg. Visitantes (gatehouse)."""

import logging
from datetime import date

from django.db import transaction
from django.utils import timezone

from core.services.validators import validate_date
from domains.gatehouse.exceptions.gatehouse_exceptions import (
    VisitorsRegisterError,
)
from domains.gatehouse.models import VisitorsRegister
from domains.residents.models import Visitor

logger = logging.getLogger(__name__)


class VisitorsRegisterService:
    """Regras de negócio dos registros de visita (criação/edição/exclusão).

    ``created_by`` recebe o usuário autenticado da gravação atual — na
    criação e também na edição (decisão de requisito do módulo 05).
    """

    REQUIRED_FIELDS = ("visitor", "visitDate")

    @staticmethod
    def _validate_required(data):
        missing = [
            f
            for f in VisitorsRegisterService.REQUIRED_FIELDS
            if not data.get(f)
        ]
        if missing:
            raise VisitorsRegisterError(
                "Campos obrigatórios ausentes: %s" % ", ".join(missing)
            )

    @staticmethod
    def _validate_visit_date(data):
        visit_date = data.get("visitDate")
        if visit_date is not None and not isinstance(visit_date, date):
            raise VisitorsRegisterError("Data da visita inválida.")
        if visit_date is not None and not validate_date(visit_date):
            raise VisitorsRegisterError("Data da visita inválida.")

    @staticmethod
    def check_duplicate(data, instance=None):
        """Impede duplicidade de visitante + data da visita."""
        visitor = data.get("visitor")
        visit_date = data.get("visitDate")
        if not visitor or not visit_date:
            return
        duplicated = VisitorsRegister.objects.filter(
            visitor=visitor,
            visitDate=visit_date,
        )
        if instance is not None and instance.pk:
            duplicated = duplicated.exclude(pk=instance.pk)
        if duplicated.exists():
            raise VisitorsRegisterError(
                "Já existe um registro de visita para este visitante "
                "nesta data."
            )

    @staticmethod
    @transaction.atomic
    def create_visit_register(data, user=None):
        """Valida e cria um registro de visita.

        ``visitDate`` é atribuída no servidor (fuso horário configurado)
        quando não informada; nenhum valor de auditoria vem do cliente.
        """
        visit_date = data.get("visitDate") or timezone.localdate()
        normalized = dict(data)
        normalized["visitDate"] = visit_date

        VisitorsRegisterService._validate_required(normalized)
        VisitorsRegisterService._validate_visit_date(normalized)

        visitor = data.get("visitor")
        if isinstance(visitor, (int, str)):
            visitor = Visitor.objects.filter(pk=visitor).first()
            if visitor is None:
                raise VisitorsRegisterError("Visitante não encontrado.")
            normalized["visitor"] = visitor

        VisitorsRegisterService.check_duplicate(normalized)

        instance = VisitorsRegister.objects.create(
            visitor=normalized["visitor"],
            visitDate=visit_date,
            observations=data.get("observations"),
            is_active=data.get("is_active", True),
            created_by=user if getattr(user, "is_authenticated", False) else None,
        )
        logger.info(
            "visit_register_created id=%s visitor=%s",
            instance.pk,
            normalized["visitor"].pk,
        )
        return instance

    @staticmethod
    @transaction.atomic
    def update_visit_register(instance, data, user=None):
        """Atualiza um registro (merge parcial) com as mesmas validações.

        ``created_by`` passa a representar o usuário desta gravação
        (decisão de requisito do módulo 05).
        """
        if instance is None:
            raise VisitorsRegisterError("Registro de visita não encontrado.")

        merged = {
            "visitor": data.get("visitor", instance.visitor),
            "visitDate": data.get("visitDate", instance.visitDate),
            "observations": data.get("observations", instance.observations),
            "is_active": data.get("is_active", instance.is_active),
        }

        if not merged["visitDate"]:
            raise VisitorsRegisterError(
                "Campos obrigatórios ausentes: visitDate"
            )
        VisitorsRegisterService._validate_visit_date(merged)

        visitor = merged["visitor"]
        if isinstance(visitor, (int, str)):
            visitor = Visitor.objects.filter(pk=visitor).first()
            if visitor is None:
                raise VisitorsRegisterError("Visitante não encontrado.")
        merged["visitor"] = visitor

        VisitorsRegisterService.check_duplicate(merged, instance=instance)

        for attr in merged:
            setattr(instance, attr, merged[attr])
        if getattr(user, "is_authenticated", False):
            instance.created_by = user
        instance.save()
        logger.info("visit_register_updated id=%s", instance.pk)
        return instance

    @staticmethod
    @transaction.atomic
    def delete_visit_register(instance):
        """Remove um registro de visita."""
        if instance is None:
            raise VisitorsRegisterError("Registro de visita não encontrado.")
        pk = instance.pk
        instance.delete()
        logger.info("visit_register_deleted id=%s", pk)

    @staticmethod
    def get_all_visit_registers():
        """Retorna todos os registros de visita."""
        return (
            VisitorsRegister.objects.select_related("visitor", "created_by")
            .order_by("-visitDate", "-id")
        )
