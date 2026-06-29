from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import DocumentType
from .forms import DocumentTypeForm

class DocumentTypeListView(LoginRequiredMixin, ListView):
    model = DocumentType
    template_name = 'parameters/document_type/list.html'
    context_object_name = 'document_types'
    paginate_by = 20

class DocumentTypeCreateView(LoginRequiredMixin, CreateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'parameters/document_type/form.html'
    success_url = reverse_lazy('document-type-list')

class DocumentTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'parameters/document_type/form.html'
    success_url = reverse_lazy('document-type-list')

class DocumentTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentType
    template_name = 'parameters/document_type/confirm_delete.html'
    success_url = reverse_lazy('document-type-list')

class DocumentTypeDetailView(LoginRequiredMixin, DetailView):
    model = DocumentType
    template_name = 'parameters/document_type/detail.html'
    context_object_name = 'document_type'
