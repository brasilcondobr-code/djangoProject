from domains.parameters.models import TypesCondominium

class TypesCondominiumRepository:
    @staticmethod
    def get_all():
        return TypesCondominium.objects.all()

    @staticmethod
    def get_by_id(id):
        try:
            return TypesCondominium.objects.get(pk=id)
        except TypesCondominium.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        types_condominium = TypesCondominium(**data)
        types_condominium.save()
        return types_condominium

    @staticmethod
    def update(types_condominium, data):
        for key, value in data.items():
            setattr(types_condominium, key, value)
        types_condominium.save()
        return types_condominium

    @staticmethod
    def delete(types_condominium):
        types_condominium.delete()
