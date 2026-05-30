from domains.gatehouse.repositories import GatehouseRepository
from domains.gatehouse.selectors import GatehouseSelector

class GatehouseService:
    @staticmethod
    def get_all_shifts():
        return GatehouseSelector.get_all_shifts()

    @staticmethod
    def get_all_service_transitions():
        return GatehouseSelector.get_all_service_transitions()

    @staticmethod
    def get_all_useful_phone_numbers():
        return GatehouseSelector.get_all_useful_phone_numbers()

    @staticmethod
    def get_all_orders():
        return GatehouseSelector.get_all_orders()

    @staticmethod
    def get_all_visitors_registers():
        return GatehouseSelector.get_all_visitors_registers()

    @staticmethod
    def get_all_correspondences():
        return GatehouseSelector.get_all_correspondences()

    @staticmethod
    def get_all_occurrences():
        return GatehouseSelector.get_all_occurrences()

    @staticmethod
    def get_all_bags():
        return GatehouseSelector.get_all_bags()

    @staticmethod
    def get_all_electronic_time_clocks():
        return GatehouseSelector.get_all_electronic_time_clocks()
