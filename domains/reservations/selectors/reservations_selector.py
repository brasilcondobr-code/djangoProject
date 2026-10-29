from domains.reservations.models import (
    Rentals, MaintenanceReservations, MoveReservations
)


class ReservationsSelector:
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
    def count_overlapping_rentals(
        *,
        unit_id,
        rental_type_id,
        status,
        start_date,
        end_date,
        exclude_pk=None,
    ):
        """Conta locações ativas com período sobreposto no escopo informado.

        O período é inclusivo: há sobreposição quando
        ``startDate <= end_date`` e ``endDate >= start_date``.
        """
        if not all((unit_id, rental_type_id, start_date, end_date)):
            return 0

        queryset = Rentals.objects.filter(
            condominium_id=unit_id,
            typesOfRentals_id=rental_type_id,
            status=status,
            is_active=True,
            startDate__lte=end_date,
            endDate__gte=start_date,
        )
        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.count()
