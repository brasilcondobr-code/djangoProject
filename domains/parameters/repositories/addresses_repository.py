from domains.parameters.models import Addresses

class AddressesRepository:
    @staticmethod
    def get_all():
        return Addresses.objects.all()

    @staticmethod
    def get_by_zip_code(zip_code):
        try:
            return Addresses.objects.get(zip_code=zip_code)
        except Addresses.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        address = Addresses(**data)
        address.save()
        return address

    @staticmethod
    def update(address, data):
        for key, value in data.items():
            setattr(address, key, value)
        address.save()
        return address

    @staticmethod
    def delete(address):
        address.delete()
