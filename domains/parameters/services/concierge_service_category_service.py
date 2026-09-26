import logging

from django.db import transaction

from domains.parameters.repositories.concierge_service_category_repository import (
    ConciergeServiceCategoryRepository,
)
from domains.parameters.validators import ParametersValidator

logger = logging.getLogger(__name__)


class ConciergeServiceCategoryService:

    @staticmethod
    def normalize_description(description):
        if description is None:
            return None
        return description.strip()

    @staticmethod
    @transaction.atomic
    def create_concierge_service_category(data):
        data = dict(data)
        data['description'] = ConciergeServiceCategoryService.normalize_description(
            data.get('description')
        )
        ParametersValidator.validate_concierge_service_category(data)

        if ConciergeServiceCategoryRepository.description_exists(data['description']):
            raise ValueError(
                'Já existe uma categoria de serviço portaria com esta descrição.'
            )

        concierge_service_category = ConciergeServiceCategoryRepository.create(data)
        logger.info(
            'concierge_service_category_created',
            extra={
                'concierge_service_category_id': concierge_service_category.pk,
                'operation': 'create',
            },
        )
        return concierge_service_category

    @staticmethod
    @transaction.atomic
    def update_concierge_service_category(concierge_service_category, data):
        data = dict(data)
        if 'description' in data:
            data['description'] = ConciergeServiceCategoryService.normalize_description(
                data.get('description')
            )
            if not data['description']:
                raise ValueError('A descrição é obrigatória.')

            if ConciergeServiceCategoryRepository.description_exists(
                data['description'], exclude_pk=concierge_service_category.pk
            ):
                raise ValueError(
                    'Já existe uma categoria de serviço portaria com esta descrição.'
                )

        updated = ConciergeServiceCategoryRepository.update(
            concierge_service_category, data
        )
        logger.info(
            'concierge_service_category_updated',
            extra={
                'concierge_service_category_id': updated.pk,
                'operation': 'update',
            },
        )
        return updated

    @staticmethod
    @transaction.atomic
    def delete_concierge_service_category(concierge_service_category):
        ConciergeServiceCategoryRepository.delete(concierge_service_category)
        logger.info(
            'concierge_service_category_deleted',
            extra={
                'concierge_service_category_id': concierge_service_category.pk,
                'operation': 'delete',
            },
        )

    @staticmethod
    @transaction.atomic
    def toggle_active(concierge_service_category, active):
        concierge_service_category.is_active = bool(active)
        concierge_service_category.save()
        logger.info(
            'concierge_service_category_status_changed',
            extra={
                'concierge_service_category_id': concierge_service_category.pk,
                'is_active': concierge_service_category.is_active,
                'operation': 'set_active',
            },
        )
        return concierge_service_category
