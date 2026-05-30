from domains.personalities.models.business_sector import BusinessSector

class BusinessSectorRepository:
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

    @staticmethod
    def list_all():
        return BusinessSector.objects.all()

    @staticmethod
    def create(data):
        business_sector = BusinessSector(**data)
        business_sector.save()
        return business_sector

    @staticmethod
    def update(business_sector, data):
        for key, value in data.items():
            setattr(business_sector, key, value)
        business_sector.save()
        return business_sector

    @staticmethod
    def delete(business_sector):
        business_sector.delete()
