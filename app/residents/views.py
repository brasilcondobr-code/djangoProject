from django.shortcuts import render
from django.http import JsonResponse
from .models import CondominiumUnit

# Create your views here.
def get_unit_identification(request):
    unit_id = request.GET.get('unit_id')
    data = {
        'identification': ''
    }
    if unit_id:
        try:
            unit = CondominiumUnit.objects.get(id=unit_id)
            data['identification'] = unit.identification or ""
        except CondominiumUnit.DoesNotExist:
            data['error'] = 'Unidade não encontrada'
    
    return JsonResponse(data)