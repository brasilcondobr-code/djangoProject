from domains.parameters.models import States

class StatesRepository:
    @staticmethod
    def get_all():
        return States.objects.all()

    @staticmethod
    def get_by_abbreviation(abbreviation):
        try:
            return States.objects.get(abbreviation=abbreviation)
        except States.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        state = States(**data)
        state.save()
        return state

    @staticmethod
    def update(state, data):
        for key, value in data.items():
            setattr(state, key, value)
        state.save()
        return state

    @staticmethod
    def delete(state):
        state.delete()
