from domains.condominium.repositories import DocumentCondominiumRepository

class DocumentCondominiumService:
    @staticmethod
    def create_document(data):
        return DocumentCondominiumRepository.create(data)

    @staticmethod
    def update_document(document_id, data):
        document = DocumentCondominiumRepository.get_by_id(document_id)
        if document:
            return DocumentCondominiumRepository.update(document, data)
        return None

    @staticmethod
    def delete_document(document_id):
        document = DocumentCondominiumRepository.get_by_id(document_id)
        if document:
            DocumentCondominiumRepository.delete(document)
            return True
        return False

    @staticmethod
    def get_document_details(document_id):
        return DocumentCondominiumRepository.get_by_id(document_id)
