from domains.residents.models import CondominiumUnit

class CondominiumUnitDTO:
    def __init__(self, id, condominium_id, tower, unit_number, floor, identification, unit_type, bedrooms, bathrooms, suites, garage_spaces, area_total, status, for_sale, for_rent, sale_price, rent_price, notes, created_at, updated_at):
        self.id = id
        self.condominium_id = condominium_id
        self.tower = tower
        self.unit_number = unit_number
        self.floor = floor
        self.identification = identification
        self.unit_type = unit_type
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.suites = suites
        self.garage_spaces = garage_spaces
        self.area_total = area_total
        self.status = status
        self.for_sale = for_sale
        self.for_rent = for_rent
        self.sale_price = sale_price
        self.rent_price = rent_price
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, unit):
        return cls(
            id=unit.id,
            condominium_id=unit.condominium.id,
            tower=unit.tower,
            unit_number=unit.unit_number,
            floor=unit.floor,
            identification=unit.identification,
            unit_type=unit.unit_type,
            bedrooms=unit.bedrooms,
            bathrooms=unit.bathrooms,
            suites=unit.suites,
            garage_spaces=unit.garage_spaces,
            area_total=unit.area_total,
            status=unit.status,
            for_sale=unit.for_sale,
            for_rent=unit.for_rent,
            sale_price=unit.sale_price,
            rent_price=unit.rent_price,
            notes=unit.notes,
            created_at=unit.created_at,
            updated_at=unit.updated_at
        )
