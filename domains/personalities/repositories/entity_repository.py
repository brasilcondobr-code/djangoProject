from domains.personalities.models.entity import Entity

class EntityRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Entity.objects.get(pk=id)
        except Entity.DoesNotExist:
            return None

    @staticmethod
    def get_by_code(code):
        try:
            return Entity.objects.get(code=code)
        except Entity.DoesNotExist:
            return None

    @staticmethod
    def get_by_cpf_cnpj(cpf_cnpj):
        try:
            return Entity.objects.get(cpf_cnpj=cpf_cnpj)
        except Entity.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Entity.objects.all()

    @staticmethod
    def get_by_business_sector(business_sector):
        return Entity.objects.filter(business_sector=business_sector)

    @staticmethod
    def create(data):
        entity = Entity(**data)
        entity.save()
        return entity

    @staticmethod
    def update(entity, data):
        for key, value in data.items():
            setattr(entity, key, value)
        entity.save()
        return entity

    @staticmethod
    def delete(entity):
        entity.delete()
