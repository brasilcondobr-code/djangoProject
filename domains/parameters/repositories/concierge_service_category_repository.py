from domains.parameters.models import ConciergeServiceCategory


class ConciergeServiceCategoryRepository:
    @staticmethod
    def get_all():
        return ConciergeServiceCategory.objects.all()

    @staticmethod
    def get_by_id(concierge_service_category_id):
        try:
            return ConciergeServiceCategory.objects.get(pk=concierge_service_category_id)
        except ConciergeServiceCategory.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        concierge_service_category = ConciergeServiceCategory(**data)
        concierge_service_category.save()
        return concierge_service_category

    @staticmethod
    def update(concierge_service_category, data):
        for key, value in data.items():
            setattr(concierge_service_category, key, value)
        concierge_service_category.save()
        return concierge_service_category

    @staticmethod
    def delete(concierge_service_category):
        concierge_service_category.delete()

    @staticmethod
    def description_exists(description, exclude_pk=None):
        queryset = ConciergeServiceCategory.objects.filter(description__iexact=description)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()
