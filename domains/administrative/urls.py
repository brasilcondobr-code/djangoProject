from django.urls import path
from domains.administrative.views import get_residents_by_type

urlpatterns = [
    path('ajax/get-residents-by-type/', get_residents_by_type, name='get_residents_by_type'),
]
