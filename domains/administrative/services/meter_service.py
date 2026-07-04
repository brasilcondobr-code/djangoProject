import logging
from django.core.exceptions import ValidationError
from domains.administrative.models.meters import Meters

logger = logging.getLogger(__name__)

class MeterService:
    @staticmethod
    def get_admin_queryset():
        return Meters.objects.select_related(
            "condominium",
            "meterType",
        )

    @staticmethod
    def calculate_consumption(previous_value, current_value):
        if previous_value is None or current_value is None:
            return None

        if current_value < previous_value:
            raise ValidationError(
                "O valor atual não pode ser menor que o valor anterior."
            )

        return current_value - previous_value

    @staticmethod
    def validate_meter_record(meter):
        if not meter:
            raise ValidationError("Registro de medidor inválido.")

        if meter.Consumption is not None and meter.Consumption < 0:
            raise ValidationError("O consumo não pode ser negativo.")

        if meter.Value is not None and meter.Value < 0:
            raise ValidationError("O valor não pode ser negativo.")

        return True
