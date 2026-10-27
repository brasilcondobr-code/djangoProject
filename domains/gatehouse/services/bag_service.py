"""Service do módulo 08. Malotes (gatehouse)."""

import logging
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from core.services.validators import validate_date
from domains.condominium.models import Collaborator, Condominium
from domains.gatehouse.exceptions.gatehouse_exceptions import BagError
from domains.gatehouse.models import Bag, BagItem

logger = logging.getLogger(__name__)


class BagService:
    """Regras de negócio dos malotes (criação/edição/exclusão).

    Sem campos de usuário de auditoria (decisão de requisito): a aba
    Auditoria contém apenas ``is_active``/``created_at``/``updated_at``.
    """

    REQUIRED_FIELDS = (
        "condominium",
        "title",
        "sender",
        "deliveryDate",
    )
    TITLE_MAX_LENGTH = 255
    RECIPIENT_MAX_LENGTH = 255
    DESCRIPTION_MAX_LENGTH = 255
    DOCUMENT_NUMBER_MAX_LENGTH = 30
    AMOUNT_MIN = 1
    AMOUNT_MAX = 999
    VALUE_MAX_DIGITS = 10
    VALUE_DECIMAL_PLACES = 2

    @staticmethod
    def server_today():
        """Data atual no fuso configurado (releaseDate na criação)."""
        return timezone.localdate()

    @staticmethod
    def _validate_required(data):
        missing = [f for f in BagService.REQUIRED_FIELDS if not data.get(f)]
        if missing:
            raise BagError(
                "Campos obrigatórios ausentes: %s" % ", ".join(missing)
            )

    @staticmethod
    def _normalize_text(data):
        """Remove espaços das bordas e exige títulos/destinatários não vazios."""
        for field, max_length in (
            ("title", BagService.TITLE_MAX_LENGTH),
            ("recipient", BagService.RECIPIENT_MAX_LENGTH),
            ("observations", None),
        ):
            value = data.get(field)
            if isinstance(value, str):
                value = value.strip()
                data[field] = value or None
            if (
                max_length
                and data.get(field)
                and len(data[field]) > max_length
            ):
                raise BagError(
                    "O campo %s deve ter no máximo %s caracteres."
                    % (field, max_length)
                )
        missing = [f for f in ("title",) if not data.get(f)]
        if missing:
            raise BagError(
                "Campos obrigatórios ausentes: %s" % ", ".join(missing)
            )

    @staticmethod
    def _validate_delivery_date(data):
        delivery = data.get("deliveryDate")
        if not validate_date(delivery):
            raise BagError("A data de entrega do malote é inválida.")

    @staticmethod
    def _resolve_condominium(condominium):
        if condominium is None or isinstance(condominium, Condominium):
            return condominium
        if isinstance(condominium, (int, str)):
            found = Condominium.objects.filter(pk=condominium).first()
            if found is None:
                raise BagError("Condomínio não encontrado.")
            return found
        raise BagError("Condomínio inválido.")

    @staticmethod
    def _resolve_sender(sender):
        if sender is None or isinstance(sender, Collaborator):
            return sender
        if isinstance(sender, (int, str)):
            found = Collaborator.objects.filter(pk=sender).first()
            if found is None:
                raise BagError("Remetente não encontrado.")
            return found
        raise BagError("Remetente inválido.")

    @staticmethod
    def validate_sender(sender, condominium):
        """Remetente deve pertencer ao condomínio selecionado (decisão 03)."""
        if (
            sender is not None
            and condominium is not None
            and sender.condominium_id != condominium.pk
        ):
            raise BagError(
                "O remetente deve pertencer ao condomínio selecionado."
            )

    @staticmethod
    def parse_value(raw):
        """Converte valor monetário pt-BR (###.###,##) em Decimal.

        A máscara do navegador é apenas visual: o backend interpreta a
        string sem depender dela (padrão do módulo bancário) e rejeita
        valores malformados, negativos ou fora da precisão de 10 dígitos
        com 2 casas decimais.
        """
        if raw in (None, ""):
            return None
        if isinstance(raw, Decimal):
            value = raw
        elif isinstance(raw, (int, float)):
            value = Decimal(str(raw))
        elif isinstance(raw, str):
            try:
                value = Decimal(raw.strip().replace(".", "").replace(",", "."))
            except InvalidOperation:
                raise BagError("Informe um valor monetário válido.")
        else:
            raise BagError("Informe um valor monetário válido.")
        if value < 0:
            raise BagError("O valor do item não pode ser negativo.")
        exponent = value.as_tuple().exponent
        if not isinstance(exponent, int) or (
            -exponent > BagService.VALUE_DECIMAL_PLACES
        ):
            raise BagError(
                "O valor deve ter no máximo %s casas decimais."
                % BagService.VALUE_DECIMAL_PLACES
            )
        if len(value.as_tuple().digits) > BagService.VALUE_MAX_DIGITS:
            raise BagError(
                "O valor deve ter no máximo %s dígitos."
                % BagService.VALUE_MAX_DIGITS
            )
        return value.quantize(Decimal("0.01"))

    @staticmethod
    def validate_item(description, amount, value=None, documentNumber=None):
        """Valida e normaliza os campos de um item de malote."""
        if isinstance(description, str):
            description = description.strip()
        if not description:
            raise BagError("A descrição do item é obrigatória.")
        if len(description) > BagService.DESCRIPTION_MAX_LENGTH:
            raise BagError(
                "A descrição do item deve ter no máximo %s caracteres."
                % BagService.DESCRIPTION_MAX_LENGTH
            )
        if isinstance(documentNumber, str):
            documentNumber = documentNumber.strip() or None
        if documentNumber and len(documentNumber) > (
            BagService.DOCUMENT_NUMBER_MAX_LENGTH
        ):
            raise BagError(
                "O número do documento deve ter no máximo %s caracteres."
                % BagService.DOCUMENT_NUMBER_MAX_LENGTH
            )
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            raise BagError(
                "A quantidade do item deve estar entre %s e %s."
                % (BagService.AMOUNT_MIN, BagService.AMOUNT_MAX)
            )
        if not BagService.AMOUNT_MIN <= amount <= BagService.AMOUNT_MAX:
            raise BagError(
                "A quantidade do item deve estar entre %s e %s."
                % (BagService.AMOUNT_MIN, BagService.AMOUNT_MAX)
            )
        return {
            "description": description,
            "documentNumber": documentNumber,
            "amount": amount,
            "value": BagService.parse_value(value),
        }

    @staticmethod
    def _validate_items(items):
        validated = []
        for item in items or []:
            if not isinstance(item, dict):
                raise BagError("Item inválido.")
            validated.append(BagService.validate_item(**item))
        return validated

    @staticmethod
    def check_duplicate(data, instance=None):
        """Impede duplicidade de condomínio + data de lançamento + título +
        remetente (decisão: só com os 4 valores presentes)."""
        condominium = data.get("condominium")
        release_date = data.get("releaseDate")
        title = data.get("title")
        sender = data.get("sender")
        if not condominium or not release_date or not title or not sender:
            return
        duplicated = Bag.objects.filter(
            condominium=condominium,
            releaseDate=release_date,
            title=title,
            sender=sender,
        )
        if instance is not None and instance.pk:
            duplicated = duplicated.exclude(pk=instance.pk)
        if duplicated.exists():
            raise BagError(
                "Já existe um malote com o mesmo condomínio, data de "
                "lançamento, título e remetente."
            )

    @staticmethod
    @transaction.atomic
    def create_bag(data, items=None):
        """Valida e cria um malote (e seus itens, atomicamente).

        ``releaseDate`` é atribuída no servidor (``timezone.localdate()``)
        na criação; nenhum valor de auditoria vem do cliente.
        """
        release_date = data.get("releaseDate") or BagService.server_today()
        normalized = dict(data)
        normalized["releaseDate"] = release_date

        BagService._validate_required(normalized)
        BagService._normalize_text(normalized)
        BagService._validate_delivery_date(normalized)

        condominium = BagService._resolve_condominium(
            data.get("condominium")
        )
        sender = BagService._resolve_sender(data.get("sender"))
        normalized["condominium"] = condominium
        normalized["sender"] = sender
        BagService.validate_sender(sender, condominium)
        BagService.check_duplicate(normalized)

        validated_items = BagService._validate_items(items)

        instance = Bag.objects.create(
            condominium=condominium,
            releaseDate=release_date,
            title=normalized["title"],
            sender=sender,
            recipient=normalized.get("recipient"),
            deliveryDate=normalized["deliveryDate"],
            handDelivery=(
                False if data.get("handDelivery") is None
                else data.get("handDelivery")
            ),
            observations=normalized.get("observations"),
            is_active=data.get("is_active", True),
        )
        for item in validated_items:
            BagItem.objects.create(bag=instance, **item)
        logger.info(
            "bag_created id=%s condominium=%s items=%s",
            instance.pk,
            condominium.pk if condominium else None,
            len(validated_items),
        )
        return instance

    @staticmethod
    @transaction.atomic
    def update_bag(instance, data, items=None):
        """Atualiza um malote (merge parcial) com as mesmas validações.

        ``items`` só é alterado quando informado explicitamente (None
        mantém os atuais; lista vazia remove todos; lista substitui).
        """
        if instance is None:
            raise BagError("Malote não encontrado.")

        merged = {
            "condominium": data.get("condominium", instance.condominium),
            "releaseDate": data.get("releaseDate", instance.releaseDate),
            "title": data.get("title", instance.title),
            "sender": data.get("sender", instance.sender),
            "recipient": data.get("recipient", instance.recipient),
            "deliveryDate": data.get("deliveryDate", instance.deliveryDate),
            "handDelivery": data.get("handDelivery", instance.handDelivery),
            "observations": data.get("observations", instance.observations),
            "is_active": data.get("is_active", instance.is_active),
        }

        BagService._validate_required(merged)
        if merged["releaseDate"] is None:
            raise BagError("A data de lançamento do malote é obrigatória.")
        BagService._normalize_text(merged)
        BagService._validate_delivery_date(merged)

        condominium = BagService._resolve_condominium(
            merged["condominium"]
        )
        sender = BagService._resolve_sender(merged["sender"])
        merged["condominium"] = condominium
        merged["sender"] = sender
        BagService.validate_sender(sender, condominium)
        BagService.check_duplicate(merged, instance=instance)

        validated_items = None
        if items is not None:
            validated_items = BagService._validate_items(items)

        for attr in merged:
            setattr(instance, attr, merged[attr])
        instance.save()

        if validated_items is not None:
            instance.items.all().delete()
            for item in validated_items:
                BagItem.objects.create(bag=instance, **item)

        logger.info("bag_updated id=%s", instance.pk)
        return instance

    @staticmethod
    @transaction.atomic
    def delete_bag(instance):
        """Remove um malote (os itens são removidos em cascata)."""
        if instance is None:
            raise BagError("Malote não encontrado.")
        pk = instance.pk
        instance.delete()
        logger.info("bag_deleted id=%s", pk)

    @staticmethod
    def get_all_bags():
        """Retorna todos os malotes com itens pré-carregados."""
        return (
            Bag.objects.select_related("condominium", "sender")
            .prefetch_related("items")
            .order_by("-releaseDate", "-id")
        )
