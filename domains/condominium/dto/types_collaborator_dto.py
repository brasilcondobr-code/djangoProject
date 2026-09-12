class TypesCollaboratorDTO:
    def __init__(self, id, name, is_active):
        self.id = id
        self.name = name
        self.is_active = is_active

    @classmethod
    def from_model(cls, types_collaborator):
        return cls(
            id=types_collaborator.id,
            name=types_collaborator.name,
            is_active=types_collaborator.is_active,
        )
