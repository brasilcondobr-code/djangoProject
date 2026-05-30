from django.shortcuts import render
from django.http import JsonResponse
from domains.residents.selectors import CondominiumUnitSelector

# Create your views here.
def get_unit_identification(request):
    unit_id = request.GET.get('unit_id')
    data = {
        'identification': ''
    }
    if unit_id:
        try:
            unit = CondominiumUnitSelector.get_by_id(unit_id)
            if unit:
                data['identification'] = unit.identification or ""
            else:
                data['error'] = 'Unidade não encontrada'
        except Exception as e:
            data['error'] = str(e)
    
    return JsonResponse(data)
