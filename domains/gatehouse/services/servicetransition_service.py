import logging

from django.db import transaction

from domains.condominium.models import Collaborator, Condominium
from domains.gatehouse.exceptions import ServiceTransitionError
from domains.gatehouse.models import ServiceTransition, ServiceTransitionObject
from domains.parameters.models import ConciergeServiceCategory

logger = logging.getLogger(__name__)


class ServiceTransitionService:
    """Serviço de domínio para operações relacionadas a passagens de serviço."""

    REQUIRED_FIELDS = ("condominium", "collaboratorEnd", "collaboratorStart", "releaseDate")

    @staticmethod
    def normalize_text(value):
        """Remove espaços desnecessários de textos livres."""
        return value.strip() if isinstance(value, str) else value

    @staticmethod
    def _validate_required(data):
        missing = [field for field in ServiceTransitionService.REQUIRED_FIELDS if not data.get(field)]
        if missing:
            raise ServiceTransitionError(
                "Campos obrigatórios ausentes: %s." % ", ".join(missing)
            )

    @staticmethod
    def _resolve_related(model, value, label, feminine=False):
        if value is None or value == "":
            raise ServiceTransitionError(
                "%s é obrigatória." % label if feminine else "%s é obrigatório." % label
            )
        instance = value if isinstance(value, model) else None
        if instance is None:
            instance = model.objects.filter(pk=value).first()
        if instance is None:
            raise ServiceTransitionError(
                "%s não encontrada." % label if feminine else "%s não encontrado." % label
            )
        return instance

    @staticmethod
    def _resolve_relations(data):
        condominium = ServiceTransitionService._resolve_related(
            Condominium, data.get("condominium"), "Condomínio"
        )
        collaborator_end = ServiceTransitionService._resolve_related(
            Collaborator, data.get("collaboratorEnd"), "Colaborador de saída"
        )
        collaborator_start = ServiceTransitionService._resolve_related(
            Collaborator, data.get("collaboratorStart"), "Colaborador de entrada"
        )
        return condominium, collaborator_end, collaborator_start

    @staticmethod
    def _ensure_unique(condominium, collaborator_end, collaborator_start, release_date, exclude_pk=None):
        qs = ServiceTransition.objects.filter(
            condominium=condominium,
            collaboratorEnd=collaborator_end,
            collaboratorStart=collaborator_start,
            releaseDate=release_date,
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        if qs.exists():
            raise ServiceTransitionError("Já existe uma passagem de serviço com esses parâmetros.")

    @staticmethod
    def validate_object_data(object_data):
        """Valida os dados de um objeto vinculado (fail fast)."""
        if not object_data:
            raise ServiceTransitionError("Os dados do objeto são obrigatórios.")
        if not ServiceTransitionService.normalize_text(object_data.get("itemObj")):
            raise ServiceTransitionError("O item do objeto é obrigatório.")
        if not object_data.get("shiftDate"):
            raise ServiceTransitionError("A data do turno do objeto é obrigatória.")

        amount = object_data.get("amountObj", 1)
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 1:
            raise ServiceTransitionError(
                "A quantidade deve ser um número inteiro maior ou igual a 1."
            )

        if not object_data.get("categoryObj"):
            raise ServiceTransitionError("A categoria do objeto é obrigatória.")
        return True

    @staticmethod
    @transaction.atomic
    def create_service_transition(data, objects_data=None, user=None):
        """Cria uma passagem de serviço com validação de regras de negócio."""
        ServiceTransitionService._validate_required(data)
        condominium, collaborator_end, collaborator_start = (
            ServiceTransitionService._resolve_relations(data)
        )
        release_date = data["releaseDate"]
        ServiceTransitionService._ensure_unique(
            condominium, collaborator_end, collaborator_start, release_date
        )

        transition = ServiceTransition.objects.create(
            condominium=condominium,
            collaboratorEnd=collaborator_end,
            collaboratorStart=collaborator_start,
            releaseDate=release_date,
            observations=ServiceTransitionService.normalize_text(data.get("observations")) or None,
            is_active=data.get("is_active", True),
            created_by=user,
        )

        for object_data in objects_data or []:
            ServiceTransitionService.add_object(transition, object_data)

        logger.info(
            "Passagem de serviço criada.",
            extra={"servicetransition_id": transition.pk, "operation": "create"},
        )
        return transition

    @staticmethod
    @transaction.atomic
    def add_object(transition, object_data):
        """Adiciona um objeto vinculado a uma passagem de serviço."""
        if transition is None or transition.pk is None:
            raise ServiceTransitionError("Passagem de serviço inválida.")

        ServiceTransitionService.validate_object_data(object_data)
        category = ServiceTransitionService._resolve_related(
            ConciergeServiceCategory, object_data.get("categoryObj"), "Categoria", feminine=True
        )

        obj = ServiceTransitionObject.objects.create(
            service_transition=transition,
            categoryObj=category,
            itemObj=ServiceTransitionService.normalize_text(object_data.get("itemObj")),
            amountObj=object_data.get("amountObj", 1),
            shiftDate=object_data.get("shiftDate"),
        )

        logger.info(
            "Objeto de passagem de serviço adicionado.",
            extra={
                "servicetransition_id": transition.pk,
                "servicetransitionobject_id": obj.pk,
                "operation": "add_object",
            },
        )
        return obj

    @staticmethod
    @transaction.atomic
    def remove_object(transition, object_pk):
        """Remove um objeto vinculado de uma passagem de serviço."""
        if transition is None or transition.pk is None:
            raise ServiceTransitionError("Passagem de serviço inválida.")

        deleted, _ = ServiceTransitionObject.objects.filter(
            pk=object_pk, service_transition=transition
        ).delete()
        if not deleted:
            raise ServiceTransitionError("Objeto vinculado não encontrado.")

        logger.info(
            "Objeto de passagem de serviço removido.",
            extra={
                "servicetransition_id": transition.pk,
                "servicetransitionobject_id": object_pk,
                "operation": "remove_object",
            },
        )

    @staticmethod
    @transaction.atomic
    def update_service_transition(transition, data, user=None):
        """Atualiza uma passagem de serviço existente."""
        if transition is None or transition.pk is None:
            raise ServiceTransitionError("Passagem de serviço inválida.")

        if data.get("condominium") or data.get("collaboratorEnd") or data.get("collaboratorStart") or data.get("releaseDate"):
            condominium = (
                ServiceTransitionService._resolve_related(
                    Condominium, data.get("condominium", transition.condominium_id), "Condomínio"
                )
            )
            collaborator_end = ServiceTransitionService._resolve_related(
                Collaborator, data.get("collaboratorEnd", transition.collaboratorEnd_id), "Colaborador de saída"
            )
            collaborator_start = ServiceTransitionService._resolve_related(
                Collaborator, data.get("collaboratorStart", transition.collaboratorStart_id), "Colaborador de entrada"
            )
            release_date = data.get("releaseDate", transition.releaseDate)
            ServiceTransitionService._ensure_unique(
                condominium, collaborator_end, collaborator_start, release_date,
                exclude_pk=transition.pk,
            )
            transition.condominium = condominium
            transition.collaboratorEnd = collaborator_end
            transition.collaboratorStart = collaborator_start
            transition.releaseDate = release_date

        if "observations" in data:
            transition.observations = (
                ServiceTransitionService.normalize_text(data.get("observations")) or None
            )
        if "is_active" in data:
            transition.is_active = data.get("is_active", transition.is_active)
        if user is not None and transition.created_by_id is None:
            transition.created_by = user

        transition.save()
        logger.info(
            "Passagem de serviço atualizada.",
            extra={"servicetransition_id": transition.pk, "operation": "update"},
        )
        return transition

    @staticmethod
    @transaction.atomic
    def delete_service_transition(transition):
        """Remove uma passagem de serviço e seus objetos (cascade)."""
        if transition is None or transition.pk is None:
            raise ServiceTransitionError("Passagem de serviço inválida.")

        transition_id = transition.pk
        transition.delete()
        logger.info(
            "Passagem de serviço removida.",
            extra={"servicetransition_id": transition_id, "operation": "delete"},
        )

    @staticmethod
    def get_service_transition_by_id(pk):
        """Busca uma passagem de serviço pelo ID."""
        transition = (
            ServiceTransition.objects.select_related(
                "condominium", "collaboratorEnd", "collaboratorStart", "created_by"
            )
            .prefetch_related("items__categoryObj")
            .filter(pk=pk)
            .first()
        )
        if transition is None:
            raise ServiceTransitionError("Passagem de serviço não encontrada.")
        return transition

    @staticmethod
    def get_all_service_transitions():
        """Retorna todas as passagens de serviço."""
        return (
            ServiceTransition.objects.select_related(
                "condominium", "collaboratorEnd", "collaboratorStart", "created_by"
            )
            .prefetch_related("items__categoryObj")
        )
