from domains.condominium.models import TypesCollaborator

class TypesCollaboratorRepository:
    @staticmethod
    def list_all():
        return TypesCollaborator.objects.all()

    @staticmethod
    def get_by_id(id):
        try:
            return TypesCollaborator.objects.get(pk=id)
        except TypesCollaborator.DoesNotExist:
            return None

    @staticmethod
    def get_active():
        return TypesCollaborator.objects.filter(is_active=True)

    @staticmethod
    def create(data):
        types_collaborator = TypesCollaborator(**data)
        types_collaborator.save()
        return types_collaborator

    @staticmethod
    def update(types_collaborator, data):
        for key, value in data.items():
            setattr(types_collaborator, key, value)
        types_collaborator.save()
        return types_collaborator

    @staticmethod
    def delete(types_collaborator):
        types_collaborator.delete()
