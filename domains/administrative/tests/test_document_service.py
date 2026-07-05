import pytest
from domains.administrative.models.documents import Documents
from domains.condominium.models import Condominium
from domains.parameters.models import DocumentType
from domains.administrative.services.document_service import DocumentService

@pytest.mark.django_db
class TestDocumentService:
    def test_document_exists_for_condominium(self, admin_user):
        condo = Condominium.objects.create(name="Condo Test")
        doc_type = DocumentType.objects.create(description="RG")
        
        Documents.objects.create(
            condominium=condo,
            document_type=doc_type,
            title="Doc 1",
            registration_date="2023-01-01",
            file="test.pdf"
        )
        
        assert DocumentService.document_exists_for_condominium(
            condominium=condo,
            title="Doc 1",
            registration_date="2023-01-01"
        ) is True
        
        assert DocumentService.document_exists_for_condominium(
            condominium=condo,
            title="Doc Diferente",
            registration_date="2023-01-01"
        ) is False

    def test_document_exists_exclude_id(self, admin_user):
        condo = Condominium.objects.create(name="Condo Test")
        doc_type = DocumentType.objects.create(description="RG")
        
        doc = Documents.objects.create(
            condominium=condo,
            document_type=doc_type,
            title="Doc 1",
            registration_date="2023-01-01",
            file="test.pdf"
        )
        
        assert DocumentService.document_exists_for_condominium(
            condominium=condo,
            title="Doc 1",
            registration_date="2023-01-01",
            exclude_id=doc.pk
        ) is False
