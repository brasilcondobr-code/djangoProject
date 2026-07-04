from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from domains.residents.models import CondominiumUnit

def get_unit_identification(request):
    unit_id = request.GET.get('id')
    if not unit_id:
        return JsonResponse({'error': 'ID não informado'}, status=400)
    
    try:
        unit = get_object_or_404(CondominiumUnit, pk=unit_id)
        
        # Construct the visual identification (Tower - Unit)
        tower = unit.tower or ''
        unit_number = unit.unit_number or ''
        visual_id = f"{tower} - {unit_number}".strip(' -') if tower and unit_number else (tower or unit_number or '')
        
        return JsonResponse({
            'identification': unit.identification or visual_id,
            'tower': tower,
            'unit_number': unit_number,
            'floor': unit.floor or '',
            'condominium': unit.condominium.name if unit.condominium else ''
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
