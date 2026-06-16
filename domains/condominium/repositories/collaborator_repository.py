from domains.condominium.models import Collaborator

class CollaboratorRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Collaborator.objects.get(pk=id)
        except Collaborator.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email):
        try:
            return Collaborator.objects.get(email=email)
        except Collaborator.DoesNotExist:
            return None

    @staticmethod
    def get_by_cpf(cpf):
        try:
            return Collaborator.objects.get(cpf=cpf)
        except Collaborator.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Collaborator.objects.all()

    @staticmethod
    def get_by_condominium(condominium):
        return Collaborator.objects.filter(condominium=condominium)

    @staticmethod
    def create(data):
        collaborator = Collaborator(**data)
        collaborator.save()
        return collaborator

    @staticmethod
    def update(collaborator, data):
        for key, value in data.items():
            setattr(collaborator, key, value)
        collaborator.save()
        return collaborator

    @staticmethod
    def delete(collaborator):
        collaborator.delete()
