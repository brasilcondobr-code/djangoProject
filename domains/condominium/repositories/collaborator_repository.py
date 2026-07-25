from shared.repositories import BaseRepository
from domains.condominium.models import Collaborator


class CollaboratorRepository(BaseRepository):
    model = Collaborator

    @classmethod
    def get_by_email(cls, email):
        try:
            return cls.model.objects.get(email=email)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_cpf(cls, cpf):
        try:
            return cls.model.objects.get(cpf=cpf)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_condominium(cls, condominium):
        return cls.model.objects.filter(condominium=condominium)
