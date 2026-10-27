from django.db import transaction
from domains.gatehouse.repositories import GatehouseRepository
from domains.gatehouse.selectors import GatehouseSelector
from domains.gatehouse.models import Shift, ShiftScale


class ShiftService:
    """Serviço de domínio para operações relacionadas a plantões."""

    @staticmethod
    @transaction.atomic
    def create_shift(data):
        """Cria um novo plantão com validação de regras de negócio."""
        # Validar datas
        if data["startDate"] > data["endDate"]:
            raise ValueError("A data final deve ser maior ou igual à data inicial.")

        # Validar unicidade
        Shift.objects.filter(
            condominium=data["condominium"],
            collaborator=data["collaborator"],
            startDate=data["startDate"],
            endDate=data["endDate"],
        ).exists() and raise ValueError(
            "Já existe um plantão com esses parâmetros."
        )

        # Criar o plantão
        shift = Shift.objects.create(
            condominium=data["condominium"],
            collaborator=data["collaborator"],
            startDate=data["startDate"],
            endDate=data["endDate"],
            title=data.get("title", ""),
            status=data.get("status"),
            is_active=data.get("is_active", True),
            created_by=request.user if "request" in data else None,
        )

        # Associar escalas, se fornecidas
        if "scales" in data:
            for scale_data in data["scales"]:
                ShiftScale.objects.create(
                    shift=shift,
                    description=scale_data.get("description", ""),
                    shiftDate=scale_data.get("shiftDate"),
                    startTime=scale_data.get("startTime"),
                    endTime=scale_data.get("endTime"),
                    is_active=scale_data.get("is_active", True),
                )

        return shift

    @staticmethod
    def get_shift_by_id(shift_id):
        """Busca um plantão pelo ID."""
        return Shift.objects.get(id=shift_id)

    @staticmethod
    def update_shift(shift_id, data):
        """Atualiza um plantão existente."""
        shift = Shift.objects.get(id=shift_id)
        shift.startDate = data.get("startDate", shift.startDate)
        shift.endDate = data.get("endDate", shift.endDate)
        shift.title = data.get("title", shift.title)
        shift.status = data.get("status", shift.status)
        shift.is_active = data.get("is_active", shift.is_active)
        shift.save()

        # Atualizar escalas, se fornecidas
        if "scales" in data:
            ShiftScale.objects.filter(shift=shift).delete()
            for scale_data in data.get("scales", []):
                ShiftScale.objects.create(
                    shift=shift,
                    description=scale_data.get("description", ""),
                    shiftDate=scale_data.get("shiftDate"),
                    startTime=scale_data.get("startTime"),
                    endTime=scale_data.get("endTime"),
                    is_active=scale_data.get("is_active", True),
                )

        return shift

    @staticmethod
    def delete_shift(shift_id):
        """Remove um plantão."""
        shift = Shift.objects.get(id=shift_id)
        shift.delete()

    @staticmethod
    def get_all_shifts():
        """Retorna todos os plantões."""
        return GatehouseSelector.get_all_shifts()

    @staticmethod
    def get_shifts_by_collaborator(collaborator_id):
        """Retorna plantões de um colaborador específico."""
        return Shift.objects.filter(collaborator_id=collaborator_id).select_related(
            "condominium", "collaborator", "status"
        )

    @staticmethod
    def get_shifts_by_condominium(condominium_id):
        """Retorna plantões de um condomínio específico."""
        return Shift.objects.filter(condominium_id=condominium_id).select_related(
            "condominium", "collaborator", "status"
        )

    @staticmethod
    def get_shifts_by_period(start_date, end_date):
        """Retorna plantões dentro de um período."""
        return Shift.objects.filter(
            startDate__lte=endDate,
            endDate__gte=start_date,
        ).select_related("condominium", "collaborator", "status")
