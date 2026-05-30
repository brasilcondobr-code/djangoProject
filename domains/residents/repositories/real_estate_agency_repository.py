from domains.residents.models import RealEstateAgency

class RealEstateAgencyRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return RealEstateAgency.objects.get(pk=id)
        except RealEstateAgency.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return RealEstateAgency.objects.all()

    @staticmethod
    def create(data):
        agency = RealEstateAgency(**data)
        agency.save()
        return agency

    @staticmethod
    def update(agency, data):
        for key, value in data.items():
            setattr(agency, key, value)
        agency.save()
        return agency

    @staticmethod
    def delete(agency):
        agency.delete()
