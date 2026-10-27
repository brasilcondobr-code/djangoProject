import logging

from django.db import transaction

from domains.parameters.repositories.types_of_rental_repository import (
    TypesOfRentalRepository,
)
from domains.parameters.validators import ParametersValidator

logger = logging.getLogger(__name__)


class TypesOfRentalService:

    @staticmethod
    def normalize_description(description):
        if description is None:
            return None
        return description.strip()

    @staticmethod
    @transaction.atomic
    def create_types_of_rental(data):
        data = dict(data)
        data['description'] = TypesOfRentalService.normalize_description(
            data.get('description')
        )
        ParametersValidator.validate_types_of_rental(data)

        if TypesOfRentalRepository.description_exists(data['description']):
            raise ValueError(
                'Já existe um tipo de locação com esta descrição.'
            )

        types_of_rental = TypesOfRentalRepository.create(data)
        logger.info(
            'types_of_rental_created',
            extra={
                'types_of_rental_id': types_of_rental.pk,
                'operation': 'create',
            },
        )
        return types_of_rental

    @staticmethod
    @transaction.atomic
    def update_types_of_rental(types_of_rental, data):
        data = dict(data)
        if 'description' in data:
            data['description'] = TypesOfRentalService.normalize_description(
                data.get('description')
            )
            if not data['description']:
                raise ValueError('A descrição é obrigatória.')

            if TypesOfRentalRepository.description_exists(
                data['description'], exclude_pk=types_of_rental.pk
            ):
                raise ValueError(
                    'Já existe um tipo de locação com esta descrição.'
                )

        updated = TypesOfRentalRepository.update(types_of_rental, data)
        logger.info(
            'types_of_rental_updated',
            extra={
                'types_of_rental_id': updated.pk,
                'operation': 'update',
            },
        )
        return updated

    @staticmethod
    @transaction.atomic
    def delete_types_of_rental(types_of_rental):
        TypesOfRentalRepository.delete(types_of_rental)
        logger.info(
            'types_of_rental_deleted',
            extra={
                'types_of_rental_id': types_of_rental.pk,
                'operation': 'delete',
            },
        )

    @staticmethod
    @transaction.atomic
    def toggle_active(types_of_rental, active):
        types_of_rental.is_active = bool(active)
        types_of_rental.save()
        logger.info(
            'types_of_rental_status_changed',
            extra={
                'types_of_rental_id': types_of_rental.pk,
                'is_active': types_of_rental.is_active,
                'operation': 'set_active',
            },
        )
        return types_of_rental
