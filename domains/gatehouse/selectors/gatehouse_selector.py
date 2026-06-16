from domains.gatehouse.models.gatehouse_models import (
    Shift, ServiceTransition, UsefulPhoneNumber, Order, 
    VisitorsRegister, Correspondence, Occurrence, Bag, ElectronicTimeClock
)

class GatehouseSelector:
    @staticmethod
    def get_all_shifts():
        return Shift.objects.all()

    @staticmethod
    def get_all_service_transitions():
        return ServiceTransition.objects.all()

    @staticmethod
    def get_all_useful_phone_numbers():
        return UsefulPhoneNumber.objects.all()

    @staticmethod
    def get_all_orders():
        return Order.objects.all()

    @staticmethod
    def get_all_visitors_registers():
        return VisitorsRegister.objects.all()

    @staticmethod
    def get_all_correspondences():
        return Correspondence.objects.all()

    @staticmethod
    def get_all_occurrences():
        return Occurrence.objects.all()

    @staticmethod
    def get_all_bags():
        return Bag.objects.all()

    @staticmethod
    def get_all_electronic_time_clocks():
        return ElectronicTimeClock.objects.all()
