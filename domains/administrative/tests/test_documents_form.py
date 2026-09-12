import pytest
from django import forms
from domains.administrative.forms import DocumentsForm
from domains.administrative.models.documents import Documents
from domains.parameters.models import DocumentType
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestDocumentsForm:
    def test_form_valid(self, _condo, admin_user):
        condo = _condo
        doc_type = DocumentType.objects.create(description="RG")
        file = SimpleUploadedFile("test.pdf", b"content")
        data = {
            'condominium': condo.pk,
            'document_type': doc_type.pk,
            'title': 'Titulo Teste',
            'registration_date': '2023-01-01',
            'is_active': True,
        }
        form = DocumentsForm(data=data, files={'file': file})
        assert form.is_valid()

    def test_form_invalid_extension(self, _condo, admin_user):
        condo = _condo
        doc_type = DocumentType.objects.create(description="RG")
        file = SimpleUploadedFile("test.exe", b"content")
        data = {
            'condominium': condo.pk,
            'document_type': doc_type.pk,
            'title': 'Titulo Teste',
            'registration_date': '2023-01-01',
        }
        form = DocumentsForm(data=data, files={'file': file})
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