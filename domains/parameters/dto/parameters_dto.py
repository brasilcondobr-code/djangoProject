from domains.parameters.models import TypesCondominium, StructionCondominium, States, Addresses, TypesVisitorRestrictions, ResidentType

class ParametersDTO:
    def __init__(self, id=None, name=None, is_active=True, created_at=None, updated_at=None,
                 abbreviation=None, capital=None, region=None,
                 zip_code=None, street=None, number=None, complement=None, neighborhood=None, city=None, country=None,
                 description=None,
                 resident_type_description=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.abbreviation = abbreviation
        self.capital = capital
        self.region = region
        self.zip_code = zip_code
        self.street = street
        self.number = number
        self.complement = complement
        self.neighborhood = neighborhood
        self.city = city
        self.country = country
        self.description = description
        self.resident_type_description = resident_type_description

    @classmethod
    def from_model(cls, model):
        if isinstance(model, TypesCondominium):
            return cls(
                id=model.id,
                name=model.name,
                is_active=model.is_active,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        elif isinstance(model, StructionCondominium):
            return cls(
                id=model.id,
                name=model.name,
                is_active=model.is_active,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        elif isinstance(model, States):
            return cls(
                id=model.id,
                name=model.name,
                abbreviation=model.abbreviation,
                capital=model.capital,
                region=model.region,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        elif isinstance(model, Addresses):
            return cls(
                id=model.id,
                zip_code=model.zip_code,
                street=model.street,
                number=model.number,
                complement=model.complement,
                neighborhood=model.neighborhood,
                city=model.city,
                country=model.country,
                is_active=model.is_active,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        elif isinstance(model, TypesVisitorRestrictions):
            return cls(
                id=model.id,
                description=model.description,
                is_active=model.is_active,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        elif isinstance(model, ResidentType):
            return cls(
                id=model.id,
                description=model.description,
                is_active=model.is_active,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        return None
