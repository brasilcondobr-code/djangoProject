import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from domains.administrative.models.patrimony import Patrimony

logger = logging.getLogger(__name__)

class PatrimonyService:
    @staticmethod
    @transaction.atomic
    def generate_asset_code(instance):
        if instance.asset_code:
            raise ValidationError("Este patrimônio já possui um código.")

        locked = Patrimony.objects.select_for_update().filter(pk=instance.pk).first()
        if locked is None:
            raise ValidationError("Patrimônio não encontrado.")
        if locked.asset_code:
            raise ValidationError("Este patrimônio já possui um código.")

        last = Patrimony.objects.filter(
            asset_code__startswith="PAT-"
        ).order_by("-asset_code").first()

        if last and last.asset_code:
            last_number = int(last.asset_code.split("-")[1])
            next_number = last_number + 1
        else:
            next_number = 1

        new_code = f"PAT-{next_number:06d}"
        instance.asset_code = new_code
        instance.save(update_fields=["asset_code"])
        logger.info("Código de patrimônio gerado: %s para o patrimônio %s", new_code, instance.pk)

        return new_code
