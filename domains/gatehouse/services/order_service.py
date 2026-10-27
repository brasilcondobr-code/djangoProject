"""Service do módulo 04. Encomendas (gatehouse)."""

import logging
from datetime import date

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.utils import timezone

from domains.gatehouse.exceptions.gatehouse_exceptions import OrderError
from domains.gatehouse.models import Order, OrderPhoto
from domains.gatehouse.validators import IMAGE_EXTENSIONS, validate_order_file
from domains.residents.models import CondominiumUnit

logger = logging.getLogger(__name__)


class OrderService:
    """Regras de negócio das encomendas (criação, leitura e exclusão)."""

    REQUIRED_FIELDS = ("unit",)

    @staticmethod
    def _validate_required(data):
        missing = [f for f in OrderService.REQUIRED_FIELDS if not data.get(f)]
        if missing:
            raise OrderError(
                "Campos obrigatórios ausentes: %s" % ", ".join(missing)
            )

    @staticmethod
    def _validate_file(file, extensions=None):
        try:
            validate_order_file(file, extensions=extensions)
        except DjangoValidationError as exc:
            raise OrderError("; ".join(exc.messages))

    @staticmethod
    def _validate_release_date(data):
        release_date = data.get("releaseDate")
        if release_date is not None and not isinstance(release_date, date):
            raise OrderError("Data de lançamento inválida.")

    @staticmethod
    def _normalize_document_number(value):
        if value is None:
            return None
        value = str(value).strip()
        return value or None

    @staticmethod
    def check_duplicate(data, instance=None):
        """Impede duplicidade de unidade + data + número do documento.

        Valores ausentes de número de documento ou de data não geram
        duplicidade (NULLs são distintos no PostgreSQL), seguindo a regra
        aprovada para o módulo.
        """
        unit = data.get("unit")
        release_date = data.get("releaseDate")
        document_number = OrderService._normalize_document_number(
            data.get("documentNumber")
        )
        if not unit or not release_date or not document_number:
            return
        duplicated = Order.objects.filter(
            unit=unit,
            releaseDate=release_date,
            documentNumber=document_number,
        )
        if instance is not None and instance.pk:
            duplicated = duplicated.exclude(pk=instance.pk)
        if duplicated.exists():
            raise OrderError(
                "Já existe uma encomenda com a mesma unidade, data de "
                "lançamento e número de documento."
            )

    @staticmethod
    @transaction.atomic
    def create_order(data, user=None, photos=None):
        """Valida e cria um registro de encomenda (e suas fotos, se houver).

        A validação ocorre antes da gravação; o arquivo só é escrito no
        armazenamento durante ``objects.create``. Uma falha posterior do
        banco dentro da transação não desfaz um arquivo já gravado — por
        isso toda validação antecede a persistência.
        """
        OrderService._validate_required(data)
        file = data.get("fileImage")
        if isinstance(file, UploadedFile):
            OrderService._validate_file(file)
        valid_photos = list(photos or [])
        for photo in valid_photos:
            if isinstance(photo, UploadedFile):
                OrderService._validate_file(
                    photo, extensions=IMAGE_EXTENSIONS
                )
        if not file and not valid_photos:
            raise OrderError(
                "Anexe o arquivo ou tire ao menos uma foto."
            )

        release_date = data.get("releaseDate") or timezone.localdate()
        OrderService._validate_release_date({"releaseDate": release_date})

        unit = data.get("unit")
        if isinstance(unit, (int, str)):
            unit = CondominiumUnit.objects.filter(pk=unit).first()
            if unit is None:
                raise OrderError("Unidade não encontrada.")

        normalized = dict(data)
        normalized["unit"] = unit
        normalized["releaseDate"] = release_date
        normalized["documentNumber"] = OrderService._normalize_document_number(
            data.get("documentNumber")
        )

        OrderService.check_duplicate(normalized)

        create_kwargs = {
            "unit": unit,
            "releaseDate": release_date,
            "documentNumber": normalized["documentNumber"],
            "observations": data.get("observations"),
            "is_active": data.get("is_active", True),
            "created_by": (
                user if getattr(user, "is_authenticated", False) else None
            ),
        }
        if file:
            create_kwargs["fileImage"] = file
        instance = Order.objects.create(**create_kwargs)
        for photo in valid_photos:
            OrderPhoto.objects.create(
                order=instance,
                file=photo,
                created_by=user if getattr(user, "is_authenticated", False) else None,
            )
        logger.info(
            "order_created id=%s unit=%s photos=%s",
            instance.pk,
            unit.pk,
            len(photos or []),
        )
        return instance

    @staticmethod
    @transaction.atomic
    def update_order(instance, data):
        """Atualiza uma encomenda (merge parcial) com as mesmas validações.

        Auditoria não é alterada aqui: ``created_by``/``created_at``
        permanecem com o autor original.
        """
        if instance is None:
            raise OrderError("Encomenda não encontrada.")

        merged = {
            "unit": data.get("unit", instance.unit),
            "releaseDate": data.get("releaseDate", instance.releaseDate),
            "documentNumber": data.get(
                "documentNumber", instance.documentNumber
            ),
            "fileImage": data.get("fileImage", instance.fileImage),
            "observations": data.get("observations", instance.observations),
            "is_active": data.get("is_active", instance.is_active),
        }

        if not merged["unit"]:
            raise OrderError("Campos obrigatórios ausentes: unit")
        if isinstance(merged["unit"], (int, str)):
            unit = CondominiumUnit.objects.filter(pk=merged["unit"]).first()
            if unit is None:
                raise OrderError("Unidade não encontrada.")
            merged["unit"] = unit

        if not merged["releaseDate"]:
            raise OrderError("Data de lançamento é obrigatória na edição.")
        OrderService._validate_release_date(merged)

        if not merged["fileImage"]:
            has_photos = OrderPhoto.objects.filter(order=instance).exists()
            if not instance.fileImage and not has_photos:
                raise OrderError(
                    "Anexe o arquivo ou tire ao menos uma foto."
                )
            merged["fileImage"] = instance.fileImage
        if isinstance(merged["fileImage"], UploadedFile):
            OrderService._validate_file(merged["fileImage"])

        merged["documentNumber"] = OrderService._normalize_document_number(
            merged["documentNumber"]
        )
        OrderService.check_duplicate(merged, instance=instance)

        for attr in merged:
            setattr(instance, attr, merged[attr])
        instance.save()
        logger.info("order_updated id=%s", instance.pk)
        return instance

    @staticmethod
    @transaction.atomic
    def delete_order(instance):
        """Remove um registro de encomenda (o arquivo não é apagado —
        comportamento consistente com os demais módulos do projeto)."""
        if instance is None:
            raise OrderError("Encomenda não encontrada.")
        pk = instance.pk
        instance.delete()
        logger.info("order_deleted id=%s", pk)

    @staticmethod
    def get_all_orders():
        """Retorna todas as encomendas."""
        return (
            Order.objects.select_related(
                "unit", "unit__condominium", "created_by"
            )
            .order_by("-releaseDate", "-id")
        )
