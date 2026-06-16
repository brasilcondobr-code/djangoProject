from domains.personalities.models.business_sector import BusinessSector

class BusinessSectorDTO:
    def __init__(self, id=None, description=None, is_active=True, created_at=None, updated_at=None):
        self.id = id
        self.description = description
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, business_sector):
        return cls(
            id=business_sector.id,
            description=business_sector.description,
            is_active=business_sector.is_active,
            created_at=business_sector.created_at,
            updated_at=business_sector.updated_at
        )
