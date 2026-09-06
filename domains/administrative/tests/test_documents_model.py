import pytest
from domains.administrative.models.documents import Documents
from domains.parameters.models import DocumentType

@pytest.mark.django_db
class TestDocumentsModel:
    def test_create_document_valid(self, _condo, admin_user):
        condo = _condo
        doc_type = DocumentType.objects.create(description="RG")
        
        doc = Documents.objects.create(
            condominium=condo,
            document_type=doc_type,
            title="Documento Teste",
            registration_date="2023-01-01",
            file="test.pdf",
            is_active=True
        )
        assert doc.title == "Documento Teste"
        assert str(doc) == "Documento Teste"

    def test_duplicate_document_fails(self, _condo, admin_user):
        condo = _condo
        doc_type = DocumentType.objects.create(description="RG")
        
        Documents.objects.create(
            condominium=condo,
            document_type=doc_type,
            title="Doc 1",
            registration_date="2023-01-01",
            file="file1.pdf"
        )
        
        with pytest.raises(Exception): # Django raises IntegrityError
            Documents.objects.create(
                condominium=condo,
                document_type=doc_type,
                title="Doc 1",
                registration_date="2023-01-01",
                file="file2.pdf"
            )
