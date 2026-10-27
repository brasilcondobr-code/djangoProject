"""Service do módulo 07. Ocorrências (gatehouse)."""

import logging
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from domains.condominium.models import Collaborator
from domains.gatehouse.exceptions.gatehouse_exceptions import OccurrenceError
from domains.gatehouse.models import Occurrence
from domains.residents.models import CondominiumUnit

logger = logging.getLogger(__name__)


class OccurrenceService:
    """Regras de negócio das ocorrências (criação/edição/exclusão).

    ``created_user`` recebe o usuário autenticado da gravação atual — na
    criação e também na edição (decisão de requisito do módulo 07).
    """

    REQUIRED_FIELDS = ("releaseDate", "subject")
    SUBJECT_MAX_LENGTH = 255

    @staticmethod
    def server_now():
        """Data/hora atuais no fuso configurado, truncada no minuto.

        O widget datetime-local opera com precisão de minuto; truncar
        mantém o valor exibido igual ao gravado e torna a unicidade
        (unidade + data/hora + assunto) efetiva na criação automática.
        """
        return timezone.now().replace(second=0, microsecond=0)

    @staticmethod
    def _validate_required(data):
        missing = [
            f for f in OccurrenceService.REQUIRED_FIELDS if not data.get(f)
        ]
        if missing:
            raise OccurrenceError(
                "Campos obrigatórios ausentes: %s" % ", ".join(missing)
            )

    @staticmethod
    def _normalize_subject(data):
        subject = data.get("subject")
        if isinstance(subject, str):
            subject = subject.strip()
            data["subject"] = subject
        if subject and len(subject) > OccurrenceService.SUBJECT_MAX_LENGTH:
            raise OccurrenceError(
                "O assunto deve ter no máximo %s caracteres."
                % OccurrenceService.SUBJECT_MAX_LENGTH
            )
        return subject

    @staticmethod
    def _validate_release_date(data):
        release_date = data.get("releaseDate")
        if release_date is None or not isinstance(release_date, datetime):
            raise OccurrenceError("Data/hora da ocorrência inválida.")

    @staticmethod
    def _resolve_unit(unit):
        if unit is None or isinstance(unit, CondominiumUnit):
            return unit
        if isinstance(unit, (int, str)):
            found = CondominiumUnit.objects.filter(pk=unit).first()
            if found is None:
                raise OccurrenceError("Unidade não encontrada.")
            return found
        raise OccurrenceError("Unidade inválida.")

    @staticmethod
    def validate_participants(participants, unit):
        """Resolve e valida participantes contra o condomínio da unidade.

        Participantes devem pertencer ao condomínio da unidade selecionada
        (decisão de requisito); sem unidade, qualquer colaborador vale.
        """
        resolved = []
        for participant in participants or []:
            if isinstance(participant, Collaborator):
                resolved.append(participant)
            else:
                found = Collaborator.objects.filter(pk=participant).first()
                if found is None:
                    raise OccurrenceError("Colaborador não encontrado.")
                resolved.append(found)
        if resolved and unit is not None:
            allowed = set(
                Collaborator.objects.filter(
                    condominium=unit.condominium
                ).values_list("pk", flat=True)
            )
            invalid = [c.name for c in resolved if c.pk not in allowed]
            if invalid:
                raise OccurrenceError(
                    "Participantes devem pertencer ao condomínio da "
                    "unidade selecionada: %s" % ", ".join(invalid)
                )
        return resolved

    @staticmethod
    def check_duplicate(data, instance=None):
        """Impede duplicidade de unidade + data/hora + assunto.

        Valores ausentes de unidade não geram duplicidade (NULLs são
        distintos no PostgreSQL), seguindo a regra aprovada (padrão 04).
        """
        unit = data.get("unit")
        release_date = data.get("releaseDate")
        subject = data.get("subject")
        if not unit or not release_date or not subject:
            return
        duplicated = Occurrence.objects.filter(
            unit=unit,
            releaseDate=release_date,
            subject=subject,
        )
        if instance is not None and instance.pk:
            duplicated = duplicated.exclude(pk=instance.pk)
        if duplicated.exists():
            raise OccurrenceError(
                "Já existe uma ocorrência com a mesma unidade, "
                "data/hora e assunto."
            )

    @staticmethod
    @transaction.atomic
    def create_occurrence(data, user=None, participants=None):
        """Valida e cria uma ocorrência (e seus participantes).

        ``releaseDate`` é atribuída no servidor (``timezone.now()``) quando
        não informada; nenhum valor de auditoria vem do cliente.
        """
        release_date = data.get("releaseDate") or OccurrenceService.server_now()
        normalized = dict(data)
        normalized["releaseDate"] = release_date

        OccurrenceService._validate_required(normalized)
        subject = OccurrenceService._normalize_subject(normalized)
        if not subject:
            raise OccurrenceError(
                "Campos obrigatórios ausentes: subject"
            )
        OccurrenceService._validate_release_date(normalized)

        unit = OccurrenceService._resolve_unit(data.get("unit"))
        normalized["unit"] = unit
        resolved_participants = OccurrenceService.validate_participants(
            participants, unit
        )
        OccurrenceService.check_duplicate(normalized)

        instance = Occurrence.objects.create(
            unit=unit,
            releaseDate=release_date,
            subject=subject,
            description=data.get("description"),
            is_active=data.get("is_active", True),
            created_user=(
                user if getattr(user, "is_authenticated", False) else None
            ),
        )
        if resolved_participants:
            instance.participants.set(resolved_participants)
        logger.info(
            "occurrence_created id=%s unit=%s participants=%s",
            instance.pk,
            unit.pk if unit else None,
            len(resolved_participants),
        )
        return instance

    @staticmethod
    @transaction.atomic
    def update_occurrence(instance, data, user=None, participants=None):
        """Atualiza uma ocorrência (merge parcial) com as mesmas validações.

        ``participants`` só é alterado quando informado explicitamente
        (None mantém os atuais). ``created_user`` passa a representar o
        usuário desta gravação (decisão de requisito do módulo 07).
        """
        if instance is None:
            raise OccurrenceError("Ocorrência não encontrada.")

        merged = {
            "unit": data.get("unit", instance.unit),
            "releaseDate": data.get("releaseDate", instance.releaseDate),
            "subject": data.get("subject", instance.subject),
            "description": data.get("description", instance.description),
            "is_active": data.get("is_active", instance.is_active),
        }

        OccurrenceService._validate_required(merged)
        subject = OccurrenceService._normalize_subject(merged)
        if not subject:
            raise OccurrenceError(
                "Campos obrigatórios ausentes: subject"
            )
        OccurrenceService._validate_release_date(merged)

        unit = OccurrenceService._resolve_unit(merged["unit"])
        merged["unit"] = unit

        resolved_participants = None
        if participants is not None:
            resolved_participants = OccurrenceService.validate_participants(
                participants, unit
            )

        OccurrenceService.check_duplicate(merged, instance=instance)

        for attr in merged:
            setattr(instance, attr, merged[attr])
        if getattr(user, "is_authenticated", False):
            instance.created_user = user
        instance.save()
        if resolved_participants is not None:
            instance.participants.set(resolved_participants)
        logger.info("occurrence_updated id=%s", instance.pk)
        return instance

    @staticmethod
    @transaction.atomic
    def delete_occurrence(instance):
        """Remove uma ocorrência (os participantes são desvinculados)."""
        if instance is None:
            raise OccurrenceError("Ocorrência não encontrada.")
        pk = instance.pk
        instance.delete()
        logger.info("occurrence_deleted id=%s", pk)

    @staticmethod
    def get_all_occurrences():
        """Retorna todas as ocorrências."""
        return (
            Occurrence.objects.select_related(
                "unit", "unit__condominium", "created_user"
            )
            .prefetch_related("participants")
            .order_by("-releaseDate", "-id")
        )
