from domains.condominium.models import Condominium
from domains.residents.models import CondominiumUnit

class CondominiumUnitRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return CondominiumUnit.objects.get(pk=id)
        except CondominiumUnit.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return CondominiumUnit.objects.all()

    @staticmethod
    def create(data):
        unit = CondominiumUnit(**data)
        unit.save()
        return unit

    @staticmethod
    def update(unit, data):
        for key, value in data.items():
            setattr(unit, key, value)
        unit.save()
        return unit

    @staticmethod
    def delete(unit):
        unit.delete()
