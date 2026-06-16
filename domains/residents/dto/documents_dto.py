from domains.residents.models import Documents

class DocumentsDTO:
    def __init__(self, id, condo_unit_id, title, document_type, file, description, is_active, created_at, updated_at):
        self.id = id
        self.condo_unit_id = condo_unit_id
        self.title = title
        self.document_type = document_type
        self.file = file
        self.description = description
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, document):
        return cls(
            id=document.id,
            condo_unit_id=document.condo_unit.id if document.condo_unit else None,
            title=document.title,
            document_type=document.document_type,
            file=document.file.name if document.file else None,
            description=document.description,
            is_active=document.is_active,
            created_at=document.created_at,
            updated_at=document.updated_at
        )
