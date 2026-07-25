from django.urls import path
from domains.administrative.views.get_residents_by_type import get_residents_by_type
from domains.administrative.views.filter_chart_options import (
    filter_classes_by_type,
    filter_groups_by_class,
    filter_subgroups_by_group,
)

urlpatterns = [
    path('ajax/residents-by-type/', get_residents_by_type, name='get_residents_by_type'),
    path('ajax/filter-classes/', filter_classes_by_type, name='filter_classes_by_type'),
    path('ajax/filter-groups/', filter_groups_by_class, name='filter_groups_by_class'),
    path('ajax/filter-subgroups/', filter_subgroups_by_group, name='filter_subgroups_by_group'),
]
