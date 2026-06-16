from domains.residents.models import Emergency

class EmergencyRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Emergency.objects.get(pk=id)
        except Emergency.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Emergency.objects.all()

    @staticmethod
    def create(data):
        emergency = Emergency(**data)
        emergency.save()
        return emergency

    @staticmethod
    def update(emergency, data):
        for key, value in data.items():
            setattr(emergency, key, value)
        emergency.save()
        return emergency

    @staticmethod
    def delete(emergency):
        emergency.delete()
