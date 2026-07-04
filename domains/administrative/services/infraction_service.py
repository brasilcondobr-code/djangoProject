import logging

from django.core.exceptions import ValidationError

from domains.administrative.models.infraction import Infraction

logger = logging.getLogger(__name__)

class InfractionService:
    @staticmethod
    def get_admin_queryset():
        return Infraction.objects.select_related(
            "infractions_type",
        ).prefetch_related("condominium")
