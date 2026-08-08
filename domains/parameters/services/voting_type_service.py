import logging

from django.db import transaction

from domains.parameters.repositories.voting_type_repository import VotingTypeRepository
from domains.parameters.validators import ParametersValidator

logger = logging.getLogger(__name__)


class VotingTypeService:

    @staticmethod
    def normalize_description(description):
        if description is None:
            return None
        return description.strip()

    @staticmethod
    @transaction.atomic
    def create_voting_type(data):
        data = dict(data)
        data['description'] = VotingTypeService.normalize_description(
            data.get('description')
        )
        ParametersValidator.validate_voting_type(data)

        if VotingTypeRepository.description_exists(data['description']):
            raise ValueError('Já existe um tipo de votação com esta descrição.')

        voting_type = VotingTypeRepository.create(data)
        logger.info(
            'voting_type_created',
            extra={
                'voting_type_id': voting_type.pk,
                'operation': 'create',
            },
        )
        return voting_type

    @staticmethod
    @transaction.atomic
    def update_voting_type(voting_type, data):
        data = dict(data)
        if 'description' in data:
            data['description'] = VotingTypeService.normalize_description(
                data.get('description')
            )
            if not data['description']:
                raise ValueError('Description is required')

            if VotingTypeRepository.description_exists(
                data['description'], exclude_pk=voting_type.pk
            ):
                raise ValueError('Já existe um tipo de votação com esta descrição.')

        updated = VotingTypeRepository.update(voting_type, data)
        logger.info(
            'voting_type_updated',
            extra={
                'voting_type_id': voting_type.pk,
                'operation': 'update',
            },
        )
        return updated

    @staticmethod
    @transaction.atomic
    def delete_voting_type(voting_type):
        VotingTypeRepository.delete(voting_type)
        logger.info(
            'voting_type_deleted',
            extra={
                'voting_type_id': voting_type.pk,
                'operation': 'delete',
            },
        )

    @staticmethod
    @transaction.atomic
    def toggle_active(voting_type, active):
        voting_type.is_active = bool(active)
        voting_type.save()
        logger.info(
            'voting_type_status_changed',
            extra={
                'voting_type_id': voting_type.pk,
                'is_active': voting_type.is_active,
                'operation': 'set_active',
            },
        )
        return voting_type