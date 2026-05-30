from domains.residents.models import Vehicle

class VehicleDTO:
    def __init__(self, id, condo_unit_id, vehicle_type, license_plate, brand, model, color, year, garage_space, photo, is_active, created_at, updated_at):
        self.id = id
        self.condo_unit_id = condo_unit_id
        self.vehicle_type = vehicle_type
        self.license_plate = license_plate
        self.brand = brand
        self.model = model
        self.color = color
        self.year = year
        self.garage_space = garage_space
        self.photo = photo
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, vehicle):
        return cls(
            id=vehicle.id,
            condo_unit_id=vehicle.condo_unit.id if vehicle.condo_unit else None,
            vehicle_type=vehicle.vehicle_type,
            license_plate=vehicle.license_plate,
            brand=vehicle.brand,
            model=vehicle.model,
            color=vehicle.color,
            year=vehicle.year,
            garage_space=vehicle.garage_space,
            photo=vehicle.photo.name if vehicle.photo else None,
            is_active=vehicle.is_active,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at
        )
