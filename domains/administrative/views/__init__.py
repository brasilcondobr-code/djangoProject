import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

from domains.parameters.models import ResidentType
from domains.residents.models import Resident

logger = logging.getLogger(__name__)


@staff_member_required
def get_residents_by_type(request):
    """
    AJAX endpoint para buscar residentes filtrados pelo tipo.
    Retorna formato próprio e formato compatível com Select2.
    """

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
                "success": False,
                "residents": [],
                "results": [],
                "count": 0,
                "message": "type_id is required",
            },
            status=400,
        )

    try:
        try:
            type_id = int(type_id_raw)
        except (ValueError, TypeError):
            resident_type = ResidentType.objects.get(description__iexact=type_id_raw)
            type_id = resident_type.id

        residents_queryset = Resident.objects.filter(
            type_of_resident_id=type_id
        ).order_by("name")

        residents_data = [
            {
                "id": resident.id,
                "name": resident.name,
                "text": resident.name,
            }
            for resident in residents_queryset
        ]

        select2_results = [
            {
                "id": resident["id"],
                "text": resident["name"],
            }
            for resident in residents_data
        ]

        logger.info(
            "Busca AJAX de residentes finalizada.",
            extra={
                "type_id_used": type_id,
                "total_residents": len(residents_data),
            },
        )

        return JsonResponse(
            {
                "success": True,
                "residents": residents_data,
                "results": select2_results,
                "count": len(residents_data),
                "message": "" if residents_data else "Nenhum residente encontrado para o tipo selecionado.",
            }
        )

    except ResidentType.DoesNotExist:
        logger.warning(f"Tipo de residente não encontrado: {type_id_raw}")

        return JsonResponse(
            {
                "success": False,
                "residents": [],
                "results": [],
                "count": 0,
                "message": "Tipo de residente não encontrado.",
            },
            status=404,
        )

    except Exception as e:
        logger.error(
            f"Erro na busca AJAX de residentes: {str(e)}",
            exc_info=True,
        )

        return JsonResponse(
            {
                "success": False,
                "residents": [],
                "results": [],
                "count": 0,
                "message": "Não foi possível carregar os residentes neste momento. Tente novamente.",
            },
            status=500,
        )
