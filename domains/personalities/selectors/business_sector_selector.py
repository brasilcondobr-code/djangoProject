from domains.personalities.models.business_sector import BusinessSector

class BusinessSectorSelector:
    @staticmethod
    def get_all():
        return BusinessSector.objects.all()

    @staticmethod
    def get_by_id(id):
        try:
            return BusinessSector.objects.get(pk=id)
        except BusinessSector.DoesNotExist:
            return None

    @staticmethod
    def get_by_description(description):
        try:
            return BusinessSector.objects.get(description=description)
        except BusinessSector.DoesNotExist:
            return None
