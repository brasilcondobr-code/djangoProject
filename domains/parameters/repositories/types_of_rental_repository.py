from domains.parameters.models import TypesOfRental


class TypesOfRentalRepository:
    @staticmethod
    def get_all():
        return TypesOfRental.objects.all()

    @staticmethod
    def get_by_id(types_of_rental_id):
        try:
            return TypesOfRental.objects.get(pk=types_of_rental_id)
        except TypesOfRental.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        types_of_rental = TypesOfRental(**data)
        types_of_rental.save()
        return types_of_rental

    @staticmethod
    def update(types_of_rental, data):
        for key, value in data.items():
            setattr(types_of_rental, key, value)
        types_of_rental.save()
        return types_of_rental

    @staticmethod
    def delete(types_of_rental):
        types_of_rental.delete()

    @staticmethod
    def description_exists(description, exclude_pk=None):
        queryset = TypesOfRental.objects.filter(description__iexact=description)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()
