from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from residents.models import CondominiumUnit

def home(request):
    return HttpResponse("<h1>Sistema Django Rodando com Sucesso! 🚀</h1><p>Ambiente Docker configurado corretamente.</p>")

def get_unit_data(request, unit_id):
    """
    API endpoint para retornar dados da unidade condominial.
    Usado para autopreencher o campo garage_space ao selecionar uma unidade.
    """
    try:
        unit = get_object_or_404(CondominiumUnit, pk=unit_id)
        return JsonResponse({
            'identification': unit.identification or '',
            'garage_spaces': unit.garage_spaces or 0,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)