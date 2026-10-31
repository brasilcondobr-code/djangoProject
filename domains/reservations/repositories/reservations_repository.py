from domains.reservations.models import (
    Rentals, MaintenanceReservations, MoveReservations
)


class ReservationsRepository:
    @staticmethod
    def get_all_rentals():
        return Rentals.objects.all()

    @staticmethod
    def get_all_maintenance_reservations():
        return MaintenanceReservations.objects.all()

    @staticmethod
    def get_maintenance_reservation_by_id(maintenance_id):
        try:
            return MaintenanceReservations.objects.select_related(
                "condominium",
                "typesOfMaintenance",
                "created_by",
                "updated_by",
            ).get(pk=maintenance_id)
        except MaintenanceReservations.DoesNotExist:
            return None

    @staticmethod
    def get_maintenance_reservation_for_update(maintenance_id):
        """Obtém a manutenção com bloqueio de linha (exige transação ativa)."""
        return MaintenanceReservations.objects.select_for_update(
            of=("self",)
        ).select_related(
            "condominium", "typesOfMaintenance"
        ).get(pk=maintenance_id)

    @staticmethod
    def create_maintenance_reservation(maintenance):
        maintenance.save()
        return maintenance

    @staticmethod
    def update_maintenance_reservation(maintenance):
        maintenance.save()
        return maintenance

    @staticmethod
    def get_all_move_reservations():
        return MoveReservations.objects.all()

    @staticmethod
    def get_move_reservation_by_id(move_id):
        try:
            return MoveReservations.objects.select_related(
                "condominium",
                "created_by",
                "updated_by",
            ).get(pk=move_id)
        except MoveReservations.DoesNotExist:
            return None

    @staticmethod
    def get_move_reservation_for_update(move_id):
        """Obtém a mudança com bloqueio de linha (exige transação ativa)."""
        return MoveReservations.objects.select_for_update(
            of=("self",)
        ).select_related("condominium").get(pk=move_id)

    @staticmethod
    def create_move_reservation(move):
        move.save()
        return move

    @staticmethod
    def update_move_reservation(move):
        move.save()
        return move

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
