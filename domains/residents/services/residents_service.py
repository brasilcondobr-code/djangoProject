from domains.residents.repositories import (
    CondominiumUnitRepository,
    ResidentRepository,
    VisitorRepository,
    RealEstateAgencyRepository,
    EmergencyRepository,
    VehicleRepository,
    AnimalRepository,
    DocumentsRepository
)
from domains.residents.selectors import (
    CondominiumUnitSelector,
    ResidentSelector,
    VisitorSelector,
    RealEstateAgencySelector,
    EmergencySelector,
    VehicleSelector,
    AnimalSelector,
    DocumentsSelector
)

class CondominiumUnitService:
    @staticmethod
    def create_unit(data):
        return CondominiumUnitRepository.create(data)

    @staticmethod
    def update_unit(unit_id, data):
        unit = CondominiumUnitRepository.get_by_id(unit_id)
        if unit:
            return CondominiumUnitRepository.update(unit, data)
        return None

    @staticmethod
    def delete_unit(unit_id):
        unit = CondominiumUnitRepository.get_by_id(unit_id)
        if unit:
            CondominiumUnitRepository.delete(unit)
            return True
        return False

class ResidentService:
    @staticmethod
    def create_resident(data):
        return ResidentRepository.create(data)

    @staticmethod
    def update_resident(resident_id, data):
        resident = ResidentRepository.get_by_id(resident_id)
        if resident:
            return ResidentRepository.update(resident, data)
        return None

    @staticmethod
    def delete_resident(resident_id):
        resident = ResidentRepository.get_by_id(resident_id)
        if resident:
            ResidentRepository.delete(resident)
            return True
        return False

    @staticmethod
    def get_resident_details(resident_id):
        return ResidentSelector.get_by_id(resident_id)

class VisitorService:
    @staticmethod
    def create_visitor(data):
        return VisitorRepository.create(data)

    @staticmethod
    def update_visitor(visitor_id, data):
        visitor = VisitorRepository.get_by_id(visitor_id)
        if visitor:
            return VisitorRepository.update(visitor, data)
        return None

    @staticmethod
    def delete_visitor(visitor_id):
        visitor = VisitorRepository.get_by_id(visitor_id)
        if visitor:
            VisitorRepository.delete(visitor)
            return True
        return False

class RealEstateAgencyService:
    @staticmethod
    def create_agency(data):
        return RealEstateAgencyRepository.create(data)

    @staticmethod
    def update_agency(agency_id, data):
        agency = RealEstateAgencyRepository.get_by_id(agency_id)
        if agency:
            return RealEstateAgencyRepository.update(agency, data)
        return None

    @staticmethod
    def delete_agency(agency_id):
        agency = RealEstateAgencyRepository.get_by_id(agency_id)
        if agency:
            RealEstateAgencyRepository.delete(agency)
            return True
        return False

class EmergencyService:
    @staticmethod
    def create_emergency(data):
        return EmergencyRepository.create(data)

    @staticmethod
    def update_emergency(emergency_id, data):
        emergency = EmergencyRepository.get_by_id(emergency_id)
        if emergency:
            return EmergencyRepository.update(emergency, data)
        return None

    @staticmethod
    def delete_emergency(emergency_id):
        emergency = EmergencyRepository.get_by_id(emergency_id)
        if emergency:
            EmergencyRepository.delete(emergency)
            return True
        return False

class VehicleService:
    @staticmethod
    def create_vehicle(data):
        return VehicleRepository.create(data)

    @staticmethod
    def update_vehicle(vehicle_id, data):
        vehicle = VehicleRepository.get_by_id(vehicle_id)
        if vehicle:
            return VehicleRepository.update(vehicle, data)
        return None

    @staticmethod
    def delete_vehicle(vehicle_id):
        vehicle = VehicleRepository.get_by_id(vehicle_id)
        if vehicle:
            VehicleRepository.delete(vehicle)
            return True
        return False

class AnimalService:
    @staticmethod
    def create_animal(data):
        return AnimalRepository.create(data)

    @staticmethod
    def update_animal(animal_id, data):
        animal = AnimalRepository.get_by_id(animal_id)
        if animal:
            return AnimalRepository.update(animal, data)
        return None

    @staticmethod
    def delete_animal(animal_id):
        animal = AnimalRepository.get_by_id(animal_id)
        if animal:
            AnimalRepository.delete(animal)
            return True
        return False

class DocumentsService:
    @staticmethod
    def create_document(data):
        return DocumentsRepository.create(data)

    @staticmethod
    def update_document(document_id, data):
        document = DocumentsRepository.get_by_id(document_id)
        if document:
            return DocumentsRepository.update(document, data)
        return None

    @staticmethod
    def delete_document(document_id):
        document = DocumentsRepository.get_by_id(document_id)
        if document:
            DocumentsRepository.delete(document)
            return True
        return False
