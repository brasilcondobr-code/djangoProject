from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import DocumentType, InfractionsType
from .forms import DocumentTypeForm, InfractionsTypeForm

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

class InfractionsTypeListView(LoginRequiredMixin, ListView):
    model = InfractionsType
    template_name = 'parameters/infractions_type/list.html'
    context_object_name = 'infractions_types'
    paginate_by = 20

class InfractionsTypeCreateView(LoginRequiredMixin, CreateView):
    model = InfractionsType
    form_class = InfractionsTypeForm
    template_name = 'parameters/infractions_type/form.html'
    success_url = reverse_lazy('infractions-type-list')

class InfractionsTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = InfractionsType
    form_class = InfractionsTypeForm
    template_name = 'parameters/infractions_type/form.html'
    success_url = reverse_lazy('infractions-type-list')

class InfractionsTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = InfractionsType
    template_name = 'parameters/infractions_type/confirm_delete.html'
    success_url = reverse_lazy('infractions-type-list')

class InfractionsTypeDetailView(LoginRequiredMixin, DetailView):
    model = InfractionsType
    template_name = 'parameters/infractions_type/detail.html'
    context_object_name = 'infractions_type'
