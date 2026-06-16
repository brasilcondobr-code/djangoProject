from domains.residents.models import Vehicle

class VehicleRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Vehicle.objects.get(pk=id)
        except Vehicle.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Vehicle.objects.all()

    @staticmethod
    def get_by_license_plate(license_plate):
        try:
            return Vehicle.objects.get(license_plate=license_plate)
        except Vehicle.DoesNotExist:
            return None

    @staticmethod
    def get_by_unit(unit):
        return Vehicle.objects.filter(condo_unit=unit)

    @staticmethod
    def create(data):
        vehicle = Vehicle(**data)
        vehicle.save()
        return vehicle

    @staticmethod
    def update(vehicle, data):
        for key, value in data.items():
            setattr(vehicle, key, value)
        vehicle.save()
        return vehicle

    @staticmethod
    def delete(vehicle):
        vehicle.delete()
