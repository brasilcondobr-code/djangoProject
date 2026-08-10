import logging

from django.db import transaction

from domains.parameters.repositories.topic_options_repository import TopicOptionRepository
from domains.parameters.validators import ParametersValidator

logger = logging.getLogger(__name__)


class TopicOptionService:

    @staticmethod
    def normalize_description(description):
        if description is None:
            return None
        return description.strip()

    @staticmethod
    @transaction.atomic
    def create_topic_option(data):
        data = dict(data)
        data['description'] = TopicOptionService.normalize_description(
            data.get('description')
        )
        ParametersValidator.validate_topic_option(data)

        if TopicOptionRepository.description_exists(data['description']):
            raise ValueError('Já existe uma opção de pauta com esta descrição.')

        topic_option = TopicOptionRepository.create(data)
        logger.info(
            'topic_option_created',
            extra={
                'topic_option_id': topic_option.pk,
                'operation': 'create',
            },
        )
        return topic_option

    @staticmethod
    @transaction.atomic
    def update_topic_option(topic_option, data):
        data = dict(data)
        if 'description' in data:
            data['description'] = TopicOptionService.normalize_description(
                data.get('description')
            )
            if not data['description']:
                raise ValueError('A descrição é obrigatória.')

            if TopicOptionRepository.description_exists(
                data['description'], exclude_pk=topic_option.pk
            ):
                raise ValueError('Já existe uma opção de pauta com esta descrição.')

        updated = TopicOptionRepository.update(topic_option, data)
        logger.info(
            'topic_option_updated',
            extra={
                'topic_option_id': topic_option.pk,
                'operation': 'update',
            },
        )
        return updated

    @staticmethod
    @transaction.atomic
    def delete_topic_option(topic_option):
        TopicOptionRepository.delete(topic_option)
        logger.info(
            'topic_option_deleted',
            extra={
                'topic_option_id': topic_option.pk,
                'operation': 'delete',
            },
        )

    @staticmethod
    @transaction.atomic
    def toggle_active(topic_option, active):
        topic_option.is_active = bool(active)
        topic_option.save()
        logger.info(
            'topic_option_status_changed',
            extra={
                'topic_option_id': topic_option.pk,
                'is_active': topic_option.is_active,
                'operation': 'set_active',
            },
        )
        return topic_option