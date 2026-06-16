from domains.residents.models import Animal

class AnimalDTO:
    def __init__(self, id, condo_unit_id, name, species, breed, age, color, gender, photo, notes, is_active, created_at, updated_at):
        self.id = id
        self.condo_unit_id = condo_unit_id
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.color = color
        self.gender = gender
        self.photo = photo
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, animal):
        return cls(
            id=animal.id,
            condo_unit_id=animal.condo_unit.id if animal.condo_unit else None,
            name=animal.name,
            species=animal.species,
            breed=animal.breed,
            age=animal.age,
            color=animal.color,
            gender=animal.gender,
            photo=animal.photo.name if animal.photo else None,
            notes=animal.notes,
            is_active=animal.is_active,
            created_at=animal.created_at,
            updated_at=animal.updated_at
        )
