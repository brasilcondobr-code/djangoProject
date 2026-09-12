import logging

from django.db import IntegrityError, transaction

from domains.administrative.exceptions import DuplicateTopicTitle
from domains.administrative.models.virtual_meeting_topic import VirtualMeetingTopic

logger = logging.getLogger(__name__)


class VirtualMeetingTopicService:

    @staticmethod
    def normalize_title(value):
        if value is None:
            return ''
        return value.strip()

    @staticmethod
    def topic_title_exists(virtual_meeting, title, exclude_pk=None):
        if virtual_meeting is None or virtual_meeting.pk is None:
            return False
        queryset = VirtualMeetingTopic.objects.filter(
            virtual_meeting=virtual_meeting,
            title__iexact=title,
        )
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()

    @staticmethod
    @transaction.atomic
    def create_topic(virtual_meeting, data):
        data = dict(data)
        data['virtual_meeting'] = virtual_meeting
        data['title'] = VirtualMeetingTopicService.normalize_title(
            data.get('title')
        )

        if not data['title']:
            raise DuplicateTopicTitle('Informe o título da pauta.')

        if VirtualMeetingTopicService.topic_title_exists(virtual_meeting, data['title']):
            raise DuplicateTopicTitle(
                'Já existe uma pauta com este título nesta assembleia.'
            )

        try:
            topic = VirtualMeetingTopic.objects.create(**data)
        except IntegrityError as exc:
            raise DuplicateTopicTitle(
                'Já existe uma pauta com este título nesta assembleia.'
            ) from exc

        logger.info(
            'virtual_meeting_topic_created',
            extra={
                'virtual_meeting_id': virtual_meeting.pk,
                'topic_id': topic.pk,
                'operation': 'create',
            },
        )
        return topic

    @staticmethod
    @transaction.atomic
    def update_topic(topic, data):
        data = dict(data)
        if 'title' in data:
            data['title'] = VirtualMeetingTopicService.normalize_title(
                data.get('title')
            )
            if not data['title']:
                raise DuplicateTopicTitle('Informe o título da pauta.')

            if VirtualMeetingTopicService.topic_title_exists(
                topic.virtual_meeting, data['title'], exclude_pk=topic.pk
            ):
                raise DuplicateTopicTitle(
                    'Já existe uma pauta com este título nesta assembleia.'
                )

        for attr, value in data.items():
            setattr(topic, attr, value)
        topic.save()
        logger.info(
            'virtual_meeting_topic_updated',
            extra={
                'virtual_meeting_id': topic.virtual_meeting_id,
                'topic_id': topic.pk,
                'operation': 'update',
            },
        )
        return topic