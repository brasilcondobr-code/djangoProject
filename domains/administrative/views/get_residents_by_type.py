from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

from domains.residents.models import Resident

@staff_member_required
def get_residents_by_type(request):
    resident_type_id = request.GET.get("type_id")

    if not resident_type_id:
        return JsonResponse(
            {
                "success": False,
                "residents": [],
                "message": "Tipo de residente não informado.",
            },
            status=400,
        )

    residents = Resident.objects.filter(
        type_of_resident_id=resident_type_id,
    ).order_by("name")

    data = [
        {
            "id": resident.id,
            "name": str(resident),
        }
        for resident in residents
    ]

    return JsonResponse(
        {
            "success": True,
            "residents": data,
        }
    )
