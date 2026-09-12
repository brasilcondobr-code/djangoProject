from domains.parameters.models import VotingType


class VotingTypeRepository:
    @staticmethod
    def get_all():
        return VotingType.objects.all()

    @staticmethod
    def get_by_id(voting_type_id):
        try:
            return VotingType.objects.get(pk=voting_type_id)
        except VotingType.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        voting_type = VotingType(**data)
        voting_type.save()
        return voting_type

    @staticmethod
    def update(voting_type, data):
        for key, value in data.items():
            setattr(voting_type, key, value)
        voting_type.save()
        return voting_type

    @staticmethod
    def delete(voting_type):
        voting_type.delete()

    @staticmethod
    def description_exists(description, exclude_pk=None):
        queryset = VotingType.objects.filter(description__iexact=description)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()