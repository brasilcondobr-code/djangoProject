from domains.parameters.models import ResidentType

class ResidentTypeRepository:
    @staticmethod
    def get_all():
        return ResidentType.objects.all()

    @staticmethod
    def get_by_id(id):
        try:
            return ResidentType.objects.get(pk=id)
        except ResidentType.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        resident_type = ResidentType(**data)
        resident_type.save()
        return resident_type

    @staticmethod
    def update(resident_type, data):
        for key, value in data.items():
            setattr(resident_type, key, value)
        resident_type.save()
        return resident_type

    @staticmethod
    def delete(resident_type):
        resident_type.delete()
