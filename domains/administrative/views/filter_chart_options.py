import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

from domains.parameters.models import Accountingclasstypes, ChartofaccountsMaingroup, ChartofaccountsSubgroup

logger = logging.getLogger(__name__)


@staff_member_required
def filter_classes_by_type(request):
    type_id = request.GET.get('type_id')
    if not type_id:
        return JsonResponse({'success': False, 'results': []}, status=400)
    try:
        classes = Accountingclasstypes.objects.filter(
            account_type_id=type_id, is_active=True,
        ).order_by('description')
        results = [{'id': c.id, 'text': str(c)} for c in classes]
        return JsonResponse({'success': True, 'results': results})
    except Exception as e:
        logger.error(f'Erro ao filtrar classes: {e}', exc_info=True)
        return JsonResponse({'success': False, 'results': []}, status=500)


@staff_member_required
def filter_groups_by_class(request):
    class_id = request.GET.get('class_id')
    if not class_id:
        return JsonResponse({'success': False, 'results': []}, status=400)
    try:
        groups = ChartofaccountsMaingroup.objects.filter(
            account_class_id=class_id, is_active=True,
        ).order_by('description')
        results = [{'id': g.id, 'text': str(g)} for g in groups]
        return JsonResponse({'success': True, 'results': results})
    except Exception as e:
        logger.error(f'Erro ao filtrar grupos: {e}', exc_info=True)
        return JsonResponse({'success': False, 'results': []}, status=500)


@staff_member_required
def filter_subgroups_by_group(request):
    group_id = request.GET.get('group_id')
    if not group_id:
        return JsonResponse({'success': False, 'results': []}, status=400)
    try:
        subgroups = ChartofaccountsSubgroup.objects.filter(
            main_group_id=group_id, is_active=True,
        ).order_by('description')
        results = [{'id': s.id, 'text': str(s)} for s in subgroups]
        return JsonResponse({'success': True, 'results': results})
    except Exception as e:
        logger.error(f'Erro ao filtrar subgrupos: {e}', exc_info=True)
        return JsonResponse({'success': False, 'results': []}, status=500)
