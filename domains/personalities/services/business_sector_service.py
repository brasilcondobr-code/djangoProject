from domains.personalities.repositories import BusinessSectorRepository
from domains.personalities.selectors import BusinessSectorSelector

class BusinessSectorService:
    @staticmethod
    def create_business_sector(data):
        return BusinessSectorRepository.create(data)

    @staticmethod
    def update_business_sector(sector_id, data):
        sector = BusinessSectorRepository.get_by_id(sector_id)
        if sector:
            return BusinessSectorRepository.update(sector, data)
        return None

    @staticmethod
    def delete_business_sector(sector_id):
        sector = BusinessSectorRepository.get_by_id(sector_id)
        if sector:
            BusinessSectorRepository.delete(sector)
            return True
        return False

    @staticmethod
    def get_all_business_sectors():
        return BusinessSectorSelector.get_all()

    @staticmethod
    def get_business_sector_by_id(id):
        return BusinessSectorSelector.get_by_id(id)
