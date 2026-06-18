import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from domains.residents.models import Resident
from domains.parameters.models import ResidentType

logger = logging.getLogger(__name__)

@staff_member_required
def get_residents_by_type(request):
    logger.info(
        "Iniciando busca AJAX de residentes por tipo.",
        extra={
            "path": request.path,
            "method": request.method,
            "query_params": dict(request.GET),
            "user_id": request.user.id if request.user.is_authenticated else None,
        },
    )

    type_id_raw = request.GET.get("type_id")

    if not type_id_raw:
        logger.warning(
            "Requisição AJAX sem type_id.",
            extra={
                "query_params": dict(request.GET),
            },
        )

        return JsonResponse(
            {
                "error": "type_id is required",
            },
            status=400,
        )

    type_id_int = None

    # Tenta converter para INT (Caminho ideal)
    try:
        type_id_int = int(type_id_raw)
        logger.info(f"type_id convertido para INT: {type_id_int}")
    except (ValueError, TypeError):
        # Se não for INT, pode ser a descrição (ex: 'Morador(a)')
        logger.info(f"type_id não é um inteiro ('{type_id_raw}'). Tentando buscar por descrição...")
        
        try:
            resident_type = ResidentType.objects.get(description=type_id_raw)
            type_id_int = resident_type.id
            logger.info(f"Tipo encontrado por descrição: {resident_type.description} (ID: {type_id_int})")
        except ResidentType.DoesNotExist:
            logger.warning(
                "type_id não é um inteiro e não corresponde a nenhuma descrição de ResidentType.",
                extra={
                    "received_value": type_id_raw,
                },
            )
            return JsonResponse(
                {
                    "error": "Invalid type_id format or description not found",
                },
                status=400,
            )

    # Executa o filtro
    residents_queryset = Resident.objects.filter(
        type_of_resident_id=type_id_int
    ).order_by("name")

    residents = list(
        residents_queryset.values(
            "id",
            "name",
            "email",
        )
    )

    logger.info(
        "Busca AJAX de residentes finalizada.",
        extra={
            "type_id_used": type_id_int,
            "total_residents": len(residents),
        },
    )

    return JsonResponse(residents, safe=False)
