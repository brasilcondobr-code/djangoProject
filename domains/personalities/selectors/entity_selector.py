from domains.personalities.models.entity import Entity

class EntitySelector:
    @staticmethod
    def get_all():
        return Entity.objects.all()

    @staticmethod
    def get_by_id(id):
        try:
            return Entity.objects.get(pk=id)
        except Entity.DoesNotExist:
            return None

    @staticmethod
    def get_by_cpf_cnpj(cpf_cnpj):
        try:
            return Entity.objects.get(cpf_cnpj=cpf_cnpj)
        except Entity.DoesNotExist:
            return None
