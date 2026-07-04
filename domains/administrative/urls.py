from django.urls import path
from domains.administrative.views.get_residents_by_type import get_residents_by_type

urlpatterns = [
    path('ajax/residents-by-type/', get_residents_by_type, name='get_residents_by_type'),
]
