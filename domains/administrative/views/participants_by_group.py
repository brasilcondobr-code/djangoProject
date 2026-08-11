import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

from domains.administrative.services.virtual_meeting_participant_service import (
    VirtualMeetingParticipantService,
)
from domains.condominium.models import Condominium
from domains.parameters.models import ResidentType

logger = logging.getLogger(__name__)

MAX_RESULTS = 500


@staff_member_required
def participants_by_group(request):
    """
    AJAX endpoint que retorna residentes pertencentes a um ou mais grupos
    de residentes (tipos de residente), no formato compatível com Select2:
    {"results": [{"id": ..., "text": ...}]}.
    """
    logger.info(
        'participants_by_group_started',
        extra={
            'path': request.path,
            'method': request.method,
            'query_params': dict(request.GET),
            'user_id': request.user.id,
        },
    )

    if request.method != 'GET':
        return JsonResponse({'detail': 'Método não permitido.'}, status=405)

    raw_group_ids = [g for g in request.GET.getlist('group_ids') if g]

    if not raw_group_ids:
        return JsonResponse({'results': []})

    try:
        group_ids = [int(g) for g in raw_group_ids]
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'Parâmetro group_ids inválido.'}, status=400)

    valid_group_ids = set(
        ResidentType.objects.filter(pk__in=group_ids).values_list('pk', flat=True)
    )
    if not valid_group_ids:
        return JsonResponse({'detail': 'Parâmetro group_ids inválido.'}, status=400)

    condominium = None
    raw_condominium_id = request.GET.get('condominium_id')
    if raw_condominium_id:
        try:
            condominium = Condominium.objects.get(pk=int(raw_condominium_id))
        except (ValueError, TypeError, Condominium.DoesNotExist):
            return JsonResponse({'detail': 'Parâmetro condominium_id inválido.'}, status=400)

    residents = VirtualMeetingParticipantService.get_residents_by_groups(
        list(valid_group_ids),
        condominium=condominium,
    )

    results = [
        {
            'id': resident.pk,
            'text': str(resident),
        }
        for resident in residents[:MAX_RESULTS]
    ]

    logger.info(
        'participants_by_group_finished',
        extra={
            'group_ids': sorted(valid_group_ids),
            'condominium_id': condominium.pk if condominium else None,
            'total_results': len(results),
        },
    )

    return JsonResponse({'results': results})
