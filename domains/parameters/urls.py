from django.urls import path
from .views import (
    DocumentTypeListView,
    DocumentTypeCreateView,
    DocumentTypeUpdateView,
    DocumentTypeDeleteView,
    DocumentTypeDetailView
)

urlpatterns = [
    path('document-type/', DocumentTypeListView.as_view(), name='document-type-list'),
    path('document-type/create/', DocumentTypeCreateView.as_view(), name='document-type-create'),
    path('document-type/update/<int:pk>/', DocumentTypeUpdateView.as_view(), name='document-type-update'),
    path('document-type/delete/<int:pk>/', DocumentTypeDeleteView.as_view(), name='document-type-delete'),
    path('document-type/detail/<int:pk>/', DocumentTypeDetailView.as_view(), name='document-type-detail'),
]
