from shared.selectors import BaseSelector
from domains.condominium.models import Collaborator


class CollaboratorSelector(BaseSelector):
    model = Collaborator

    @classmethod
    def get_by_email(cls, email):
        return cls.model.objects.filter(email=email).first()

    @classmethod
    def get_by_cpf(cls, cpf):
        return cls.model.objects.filter(cpf=cpf).first()

    @classmethod
    def get_by_condominium(cls, condominium):
        return cls.model.objects.filter(condominium=condominium)
