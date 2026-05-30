from domains.parameters.models import StructionCondominium

class StructionCondominiumRepository:
    @staticmethod
    def get_all():
        return StructionCondominium.objects.all()

    @staticmethod
    def get_by_id(id):
        try:
            return StructionCondominium.objects.get(pk=id)
        except StructionCondominium.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        struction_condominium = StructionCondominium(**data)
        struction_condominium.save()
        return struction_condominium

    @staticmethod
    def update(struction_condominium, data):
        for key, value in data.items():
            setattr(struction_condominium, key, value)
        struction_condominium.save()
        return struction_condominium

    @staticmethod
    def delete(struction_condominium):
        struction_condominium.delete()
