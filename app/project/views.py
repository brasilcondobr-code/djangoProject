import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from domains.residents.models import CondominiumUnit, Resident, Vehicle, Animal, Visitor
from domains.condominium.models import Condominium, Collaborator
from personalities.models import Entity
from domains.parameters.models import Addresses

# Cidade padrão para fallback (ambiente local ou falha na geolocalização)
DEFAULT_CITY = 'Campinas'

def home(request):
    return HttpResponse("<h1>Sistema Django Rodando com Sucesso! 🚀</h1><p>Ambiente Docker configurado corretamente.</p>")

def get_condo_indicators(request):
    """
    Retorna o total de registros de cada entidade do sistema.
    """
    try:
        indicators = {
            'unidades': CondominiumUnit.objects.count(),
            'colaboradores': Collaborator.objects.count(),
            'moradores': Resident.objects.count(),
            'veiculos': Vehicle.objects.count(),
            'animais': Animal.objects.count(),
            'entidades': Entity.objects.count(),
        }
        return JsonResponse(indicators)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_weather_cities(request):
    """
    Retorna uma lista de cidades e estados únicos cadastrados para a previsão do tempo.
    """
    addresses = Addresses.objects.values('city', 'state__abbreviation').distinct()
    city_list = [
        {'city': item['city'], 'state': item['state__abbreviation']} 
        for item in addresses
    ]
    return JsonResponse(city_list, safe=False)

def get_weather_by_ip(request):
    """
    Identifica a cidade do usuário via IP e retorna a previsão do tempo da HG Brasil.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if ip == '127.0.0.1' or ip == '::1':
        city_name = DEFAULT_CITY
    else:
        try:
            geo_res = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json()
            if geo_res.get('status') == 'success':
                city_name = geo_res.get('city')
            else:
                city_name = DEFAULT_CITY
        except Exception:
            city_name = DEFAULT_CITY

    api_key = '0b9eb325'
    weather_url = f'https://api.hgbrasil.com/weather?key={api_key}&city={city_name}'
    
    try:
        weather_res = requests.get(weather_url, timeout=10).json()
        if weather_res.get('results'):
            return JsonResponse(weather_res)
        return JsonResponse({'error': f'Clima para {city_name} não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_weather(request):
    """
    Proxy para a API da HG Brasil para evitar erros de CORS.
    """
    city = request.GET.get('city')
    state = request.GET.get('state', '')
    if not city:
        return JsonResponse({'error': 'Cidade não informada'}, status=400)
    
    query = f"{city},{state}" if state else city
    api_key = '0b9eb325'
    url = f'https://api.hgbrasil.com/weather?key={api_key}&city={query}'
    
    try:
        response = requests.get(url, timeout=10).json()
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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

def get_weather_cities(request):
    """
    Retorna uma lista de cidades e estados únicos cadastrados para a previsão do tempo.
    """
    addresses = Addresses.objects.values('city', 'state__abbreviation').distinct()
    city_list = [
        {'city': item['city'], 'state': item['state__abbreviation']} 
        for item in addresses
    ]
    return JsonResponse(city_list, safe=False)

def get_weather_by_ip(request):
    """
    Identifica a cidade do usuário via IP e retorna a previsão do tempo da HG Brasil.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if ip == '127.0.0.1' or ip == '::1':
        city_name = DEFAULT_CITY
    else:
        try:
            geo_res = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json()
            if geo_res.get('status') == 'success':
                city_name = geo_res.get('city')
            else:
                city_name = DEFAULT_CITY
        except Exception:
            city_name = DEFAULT_CITY

    api_key = '0b9eb325'
    weather_url = f'https://api.hgbrasil.com/weather?key={api_key}&city={city_name}'
    
    try:
        weather_res = requests.get(weather_url, timeout=10).json()
        if weather_res.get('results'):
            return JsonResponse(weather_res)
        return JsonResponse({'error': f'Clima para {city_name} não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_weather(request):
    """
    Proxy para a API da HG Brasil para evitar erros de CORS.
    """
    city = request.GET.get('city')
    state = request.GET.get('state', '')
    if not city:
        return JsonResponse({'error': 'Cidade não informada'}, status=400)
    
    query = f"{city},{state}" if state else city
    api_key = '0b9eb325'
    url = f'https://api.hgbrasil.com/weather?key={api_key}&city={query}'
    
    try:
        response = requests.get(url, timeout=10).json()
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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

def get_weather(request):
    """
    Proxy para a API da HG Brasil para evitar erros de CORS.
    """
    city = request.GET.get('city')
    state = request.GET.get('state', '')
    if not city:
        return JsonResponse({'error': 'Cidade não informada'}, status=400)
    
    # Para maior precisão na HG Brasil, usamos "Cidade,UF"
    query = f"{city},{state}" if state else city
    api_key = '0b9eb325'
    url = f'https://api.hgbrasil.com/weather?key={api_key}&city={query}'
    
    try:
        response = requests.get(url, timeout=10).json()
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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