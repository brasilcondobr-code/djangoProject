from domains.reservations.models import (
    Rentals, MaintenanceReservations, MoveReservations, Reforms
)

class ReservationsRepository:
    @staticmethod
    def get_all_rentals():
        return Rentals.objects.all()

    @staticmethod
    def get_all_maintenance_reservations():
        return MaintenanceReservations.objects.all()

    @staticmethod
    def get_all_move_reservations():
        return MoveReservations.objects.all()

    @staticmethod
    def get_all_reforms():
        return Reforms.objects.all()
