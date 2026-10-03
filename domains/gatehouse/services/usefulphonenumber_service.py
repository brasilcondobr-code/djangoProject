"""Service do módulo 03. Telefones Úteis (gatehouse)."""

import logging

from django.db import transaction

from core.services.validators import validate_date, validate_phone
from domains.gatehouse.exceptions.gatehouse_exceptions import (
    UsefulPhoneNumberError,
)
from domains.gatehouse.models import UsefulPhoneNumber
from domains.parameters.models import CategoryPhone
from domains.condominium.models import Condominium

logger = logging.getLogger(__name__)


class UsefulPhoneNumberService:
    """Regras de negócio dos telefones úteis (sem edição: criação/exclusão)."""

    REQUIRED_FIELDS = (
        "condominium",
        "categoryPhone",
        "releaseDate",
        "name",
        "phone1",
    )
    PHONE_FIELDS = ("phone1", "phone2", "phone3", "phone4", "phone5")

    @staticmethod
    def _validate_required(data):
        missing = [f for f in UsefulPhoneNumberService.REQUIRED_FIELDS if not data.get(f)]
        if missing:
            raise UsefulPhoneNumberError(
                "Campos obrigatórios ausentes: %s" % ", ".join(missing)
            )

    @staticmethod
    def _validate_phones(data):
        for field in UsefulPhoneNumberService.PHONE_FIELDS:
            phone = data.get(field)
            if phone and not validate_phone(phone):
                raise UsefulPhoneNumberError(
                    "Telefone inválido no campo %s. Use o formato: (99) 99999-9999."
                    % field
                )

    @staticmethod
    def _validate_release_date(data):
        release_date = data.get("releaseDate")
        if release_date and not validate_date(release_date):
            raise UsefulPhoneNumberError(
                "Data de lançamento inválida. Use o formato: dd/mm/aaaa."
            )

    @staticmethod
    def _check_duplicates(data, instance=None):
        duplicated = UsefulPhoneNumber.objects.filter(
            condominium=data.get("condominium"),
            categoryPhone=data.get("categoryPhone"),
            name=data.get("name"),
            releaseDate=data.get("releaseDate"),
        )
        if instance is not None and instance.pk:
            duplicated = duplicated.exclude(pk=instance.pk)
        if duplicated.exists():
            raise UsefulPhoneNumberError(
                "Já existe um telefone útil com os mesmos condomínio, "
                "categoria, nome e data de lançamento."
            )

    @staticmethod
    @transaction.atomic
    def create_useful_phone_number(data, user=None):
        """Valida e cria um registro de telefone útil."""
        UsefulPhoneNumberService._validate_required(data)
        UsefulPhoneNumberService._validate_phones(data)
        UsefulPhoneNumberService._validate_release_date(data)

        condominium = data.get("condominium")
        if isinstance(condominium, (int, str)):
            condominium = Condominium.objects.filter(pk=condominium).first()
            if condominium is None:
                raise UsefulPhoneNumberError("Condomínio não encontrado.")
        category = data.get("categoryPhone")
        if isinstance(category, (int, str)):
            category = CategoryPhone.objects.filter(pk=category).first()
            if category is None:
                raise UsefulPhoneNumberError("Categoria de telefone não encontrada.")

        normalized = dict(data)
        name = normalized.get("name")
        if isinstance(name, str):
            normalized["name"] = name.strip()
        normalized["condominium"] = condominium
        normalized["categoryPhone"] = category

        UsefulPhoneNumberService._check_duplicates(normalized)

        instance = UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category,
            releaseDate=normalized.get("releaseDate"),
            name=normalized["name"],
            phone1=normalized.get("phone1", ""),
            phone2=normalized.get("phone2", ""),
            phone3=normalized.get("phone3", ""),
            phone4=normalized.get("phone4", ""),
            phone5=normalized.get("phone5", ""),
            observations=normalized.get("observations"),
            is_active=normalized.get("is_active", True),
            created_by=user if getattr(user, "is_authenticated", False) else None,
        )
        logger.info("useful_phone_number_created id=%s", instance.pk)
        return instance

    @staticmethod
    @transaction.atomic
    def delete_useful_phone_number(instance):
        """Remove um registro de telefone útil."""
        if instance is None:
            raise UsefulPhoneNumberError("Telefone útil não encontrado.")
        pk = instance.pk
        instance.delete()
        logger.info("useful_phone_number_deleted id=%s", pk)

    @staticmethod
    def get_all_useful_phone_numbers():
        """Retorna todos os telefones úteis."""
        return (
            UsefulPhoneNumber.objects.select_related(
                "condominium", "categoryPhone", "created_by"
            )
            .order_by("name", "id")
        )
