from domains.residents.models import Resident

class ResidentRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Resident.objects.get(pk=id)
        except Resident.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email):
        try:
            return Resident.objects.get(email=email)
        except Resident.DoesNotExist:
            return None

    @staticmethod
    def get_by_cpf(cpf):
        try:
            return Resident.objects.get(cpf=cpf)
        except Resident.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Resident.objects.all()

    @staticmethod
    def get_by_unit(unit):
        return Resident.objects.filter(unit=unit)

    @staticmethod
    def create(data):
        resident = Resident(**data)
        resident.save()
        return resident

    @staticmethod
    def update(resident, data):
        for key, value in data.items():
            setattr(resident, key, value)
        resident.save()
        return resident

    @staticmethod
    def delete(resident):
        resident.delete()
