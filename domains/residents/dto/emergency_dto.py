from domains.residents.models import Emergency

class EmergencyDTO:
    def __init__(self, id, condo_unit_id, type, description, occurred_at, is_active, created_at, updated_at):
        self.id = id
        self.condo_unit_id = condo_unit_id
        self.type = type
        self.description = description
        self.occurred_at = occurred_at
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, emergency):
        return cls(
            id=emergency.id,
            condo_unit_id=emergency.condo_unit.id if emergency.condo_unit else None,
            type=emergency.type,
            description=emergency.description,
            occurred_at=emergency.occurred_at,
            is_active=emergency.is_active,
            created_at=emergency.created_at,
            updated_at=emergency.updated_at
        )
