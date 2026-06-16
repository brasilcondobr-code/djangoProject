from domains.condominium.models import Collaborator

class CollaboratorSelector:
    @staticmethod
    def get_all_active():
        return Collaborator.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(id):
        return Collaborator.objects.filter(pk=id).first()

    @staticmethod
    def get_by_email(email):
        return Collaborator.objects.filter(email=email).first()

    @staticmethod
    def get_by_cpf(cpf):
        return Collaborator.objects.filter(cpf=cpf).first()

    @staticmethod
    def get_by_condominium(condominium):
        return Collaborator.objects.filter(condominium=condominium)
