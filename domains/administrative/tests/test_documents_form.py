import pytest
from django import forms
from domains.administrative.forms import DocumentsForm
from domains.administrative.models.documents import Documents
from domains.condominium.models import Condominium
from domains.parameters.models import DocumentType
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
class TestDocumentsForm:
    def test_form_valid(self, admin_user):
        condo = Condominium.objects.create(name="Condo Test")
        doc_type = DocumentType.objects.create(description="RG")
        file = SimpleUploadedFile("test.pdf", b"content")
        
        data = {
            'condominium': condo.pk,
            'document_type': doc_type.pk,
            'title': 'Titulo Teste',
            'registration_date': '2023-01-01',
            'file': file,
            'is_active': True
        }
        form = DocumentsForm(data=data)
        assert form.is_valid()

    def test_form_invalid_extension(self, admin_user):
        condo = Condominium.objects.create(name="Condo Test")
        doc_type = DocumentType.objects.create(description="RG")
        file = SimpleUploadedFile("test.exe", b"content")
        
        data = {
            'condominium': condo.pk,
            'document_type': doc_type.pk,
            'title': 'Titulo Teste',
            'registration_date': '2023-01-01',
            'file': file,
        }
        form = DocumentsForm(data=data)
        assert not form.is_valid()
        assert 'file' in form.errors

    def test_form_invalid_required_fields(self, admin_user):
        form = DocumentsForm(data={})
        assert not form.is_valid()
        assert 'condominium' in form.errors
        assert 'document_type' in form.errors
        assert 'title' in form.errors
        assert 'registration_date' in form.errors
        assert 'file' in form.errors
