from django.urls import path
from .views import (
    DocumentTypeListView,
    DocumentTypeCreateView,
    DocumentTypeUpdateView,
    DocumentTypeDeleteView,
    DocumentTypeDetailView,
    InfractionsTypeListView,
    InfractionsTypeCreateView,
    InfractionsTypeUpdateView,
    InfractionsTypeDeleteView,
    InfractionsTypeDetailView
)

urlpatterns = [
    path('document-type/', DocumentTypeListView.as_view(), name='document-type-list'),
    path('document-type/create/', DocumentTypeCreateView.as_view(), name='document-type-create'),
    path('document-type/update/<int:pk>/', DocumentTypeUpdateView.as_view(), name='document-type-update'),
    path('document-type/delete/<int:pk>/', DocumentTypeDeleteView.as_view(), name='document-type-delete'),
    path('document-type/detail/<int:pk>/', DocumentTypeDetailView.as_view(), name='document-type-detail'),
    path('infractions-type/', InfractionsTypeListView.as_view(), name='infractions-type-list'),
    path('infractions-type/create/', InfractionsTypeCreateView.as_view(), name='infractions-type-create'),
    path('infractions-type/update/<int:pk>/', InfractionsTypeUpdateView.as_view(), name='infractions-type-update'),
    path('infractions-type/delete/<int:pk>/', InfractionsTypeDeleteView.as_view(), name='infractions-type-delete'),
    path('infractions-type/detail/<int:pk>/', InfractionsTypeDetailView.as_view(), name='infractions-type-detail'),
]
