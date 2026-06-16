from domains.residents.models import Animal

class AnimalRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Animal.objects.get(pk=id)
        except Animal.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Animal.objects.all()

    @staticmethod
    def get_by_unit(unit):
        return Animal.objects.filter(condo_unit=unit)

    @staticmethod
    def create(data):
        animal = Animal(**data)
        animal.save()
        return animal

    @staticmethod
    def update(animal, data):
        for key, value in data.items():
            setattr(animal, key, value)
        animal.save()
        return animal

    @staticmethod
    def delete(animal):
        animal.delete()
