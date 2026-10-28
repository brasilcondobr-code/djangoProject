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

    @staticmethod
    def get_rental_by_id(rental_id):
        try:
            return Rentals.objects.select_related(
                "condominium", "typesOfRentals", "created_by", "updated_by"
            ).get(pk=rental_id)
        except Rentals.DoesNotExist:
            return None

    @staticmethod
    def get_rental_for_update(rental_id):
        """Obtém a locação com bloqueio de linha (exige transação ativa)."""
        return Rentals.objects.select_for_update(of=("self",)).select_related(
            "condominium", "typesOfRentals"
        ).get(pk=rental_id)

    @staticmethod
    def set_error_status(rental_id, message):
        """Persiste o motivo da rejeição sem alterar os demais campos."""
        return Rentals.objects.filter(pk=rental_id).update(errorStatus=message)

    @staticmethod
    def create_rental(rental):
        rental.save()
        return rental

    @staticmethod
    def update_rental(rental):
        rental.save()
        return rental
