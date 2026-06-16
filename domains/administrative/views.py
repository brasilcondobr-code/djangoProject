from django.http import JsonResponse
from domains.residents.models import Resident

def get_residents_by_type(request):
    type_id = request.GET.get('type_id')
    if not type_id:
        return JsonResponse({'error': 'type_id is required'}, status=400)
    
    # Ensure type_id is treated as an integer for the filter
    try:
        type_id_int = int(type_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid type_id format'}, status=400)

    residents = Resident.objects.filter(type_of_resident_id=type_id_int).values('id', 'name', 'email')
    return JsonResponse(list(residents), safe=False)
