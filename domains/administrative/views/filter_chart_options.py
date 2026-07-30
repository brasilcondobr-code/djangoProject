import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

from domains.administrative.services.chartofaccount_service import ChartOfAccountService

logger = logging.getLogger(__name__)


@staff_member_required
def filter_classes_by_type(request):
    tipo_conta_id = request.GET.get('tipo_conta_id')
    if not tipo_conta_id:
        return JsonResponse({'results': []}, status=400)
    try:
        tipo_conta_id = int(tipo_conta_id)
    except (ValueError, TypeError):
        return JsonResponse({'results': []}, status=400)
    try:
        classes = ChartOfAccountService.get_classes_by_type(tipo_conta_id)
        results = []
        for c in classes:
            text = f"{c['code']} - {c['description']}"
            tipo = c.get('account_type__description')
            if tipo:
                text += f" ({tipo})"
            results.append({'id': c['id'], 'text': text})
        return JsonResponse({'results': results})
    except Exception as e:
        logger.error('Erro ao filtrar classes por tipo %s: %s', tipo_conta_id, e, exc_info=True)
        return JsonResponse({'results': []}, status=500)


@staff_member_required
def filter_groups_by_class(request):
    classe_contabil_id = request.GET.get('classe_contabil_id')
    if not classe_contabil_id:
        return JsonResponse({'results': []}, status=400)
    try:
        classe_contabil_id = int(classe_contabil_id)
    except (ValueError, TypeError):
        return JsonResponse({'results': []}, status=400)
    try:
        groups = ChartOfAccountService.get_groups_by_class(classe_contabil_id)
        results = []
        for g in groups:
            text = f"{g['code']} - {g['description']}"
            cls_code = g.get('account_class__code')
            cls_desc = g.get('account_class__description')
            cls_tipo = g.get('account_class__account_type__description')
            parts = [text]
            if cls_desc:
                parts.append(cls_desc)
            if cls_tipo:
                parts.append(cls_tipo)
            results.append({'id': g['id'], 'text': ' / '.join(parts)})
        return JsonResponse({'results': results})
    except Exception as e:
        logger.error('Erro ao filtrar grupos por classe %s: %s', classe_contabil_id, e, exc_info=True)
        return JsonResponse({'results': []}, status=500)


@staff_member_required
def filter_subgroups_by_group(request):
    grupo_principal_id = request.GET.get('grupo_principal_id')
    if not grupo_principal_id:
        return JsonResponse({'results': []}, status=400)
    try:
        grupo_principal_id = int(grupo_principal_id)
    except (ValueError, TypeError):
        return JsonResponse({'results': []}, status=400)
    try:
        subgroups = ChartOfAccountService.get_subgroups_by_group(grupo_principal_id)
        results = []
        for s in subgroups:
            text = f"{s['code']} - {s['description']}"
            grp_code = s.get('main_group__code')
            grp_desc = s.get('main_group__description')
            grp_cls = s.get('main_group__account_class__description')
            parts = [text]
            if grp_desc:
                parts.append(grp_desc)
            if grp_cls:
                parts.append(grp_cls)
            results.append({'id': s['id'], 'text': ' / '.join(parts)})
        return JsonResponse({'results': results})
    except Exception as e:
        logger.error('Erro ao filtrar subgrupos por grupo %s: %s', grupo_principal_id, e, exc_info=True)
        return JsonResponse({'results': []}, status=500)
