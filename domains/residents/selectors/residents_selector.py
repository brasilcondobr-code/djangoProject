from domains.residents.models import CondominiumUnit, Resident, Visitor, RealEstateAgency, Emergency, Vehicle, Animal, Documents

class CondominiumUnitSelector:
    @staticmethod
    def get_all():
        return CondominiumUnit.objects.all()

    @staticmethod
    def get_by_id(id):
        return CondominiumUnit.objects.filter(pk=id).first()

    @staticmethod
    def get_by_tower_and_number(tower, unit_number):
        return CondominiumUnit.objects.filter(tower=tower, unit_number=unit_number).first()

class ResidentSelector:
    @staticmethod
    def get_all_active():
        return Resident.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(id):
        return Resident.objects.filter(pk=id).first()

    @staticmethod
    def get_by_email(email):
        return Resident.objects.filter(email=email).first()

    @staticmethod
    def get_by_cpf(cpf):
        return Resident.objects.filter(cpf=cpf).first()

    @staticmethod
    def get_by_unit(unit):
        return Resident.objects.filter(unit=unit)

class VisitorSelector:
    @staticmethod
    def get_all():
        return Visitor.objects.all()

    @staticmethod
    def get_by_id(id):
        return Visitor.objects.filter(pk=id).first()

    @staticmethod
    def get_by_condo_unit(condo_unit):
        return Visitor.objects.filter(condo_unit=condo_unit)

class RealEstateAgencySelector:
    @staticmethod
    def get_all():
        return RealEstateAgency.objects.all()

    @staticmethod
    def get_by_id(id):
        return RealEstateAgency.objects.filter(pk=id).first()

class EmergencySelector:
    @staticmethod
    def get_all():
        return Emergency.objects.all()

    @staticmethod
    def get_by_id(id):
        return Emergency.objects.filter(pk=id).first()

    @staticmethod
    def get_by_condo_unit(condo_unit):
        return Emergency.objects.filter(condo_unit=condo_unit)

class VehicleSelector:
    @staticmethod
    def get_all():
        return Vehicle.objects.all()

    @staticmethod
    def get_by_id(id):
        return Vehicle.objects.filter(pk=id).first()

    @staticmethod
    def get_by_license_plate(license_plate):
        return Vehicle.objects.filter(license_plate=license_plate).first()

    @staticmethod
    def get_by_condo_unit(condo_unit):
        return Vehicle.objects.filter(condo_unit=condo_unit)

class AnimalSelector:
    @staticmethod
    def get_all():
        return Animal.objects.all()

    @staticmethod
    def get_by_id(id):
        return Animal.objects.filter(pk=id).first()

    @staticmethod
    def get_by_condo_unit(condo_unit):
        return Animal.objects.filter(condo_unit=condo_unit)

class DocumentsSelector:
    @staticmethod
    def get_all():
        return Documents.objects.all()

    @staticmethod
    def get_by_id(id):
        return Documents.objects.filter(pk=id).first()

    @staticmethod
    def get_by_condo_unit(condo_unit):
        return Documents.objects.filter(condo_unit=condo_unit)
