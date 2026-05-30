from domains.reservations.repositories import ReservationsRepository
from domains.reservations.selectors import ReservationsSelector

class ReservationsService:
    @staticmethod
    def get_all_rentals():
        return ReservationsSelector.get_all_rentals()

    @staticmethod
    def get_all_maintenance_reservations():
        return ReservationsSelector.get_all_maintenance_reservations()

    @staticmethod
    def get_all_move_reservations():
        return ReservationsSelector.get_all_move_reservations()

    @staticmethod
    def get_all_reforms():
        return ReservationsSelector.get_all_reforms()
