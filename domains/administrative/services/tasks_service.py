import logging

from django.db import transaction
from django.core.exceptions import ValidationError

from domains.administrative.models.task import Task
from domains.administrative.validators import validate_task_title, validate_task_description

logger = logging.getLogger(__name__)


class TaskService:

    @staticmethod
    @transaction.atomic
    def create_task(user, validated_data):
        task = Task.objects.create(**validated_data)
        logger.info(
            'task_created',
            extra={
                'task_id': task.pk,
                'condominium_id': task.condominium_id,
                'responsible_user_id': task.responsible_user_id,
                'actor_user_id': user.pk if user else None,
                'operation': 'create',
            },
        )
        return task

    @staticmethod
    @transaction.atomic
    def update_task(user, task, validated_data):
        for attr, value in validated_data.items():
            setattr(task, attr, value)
        task.save()
        logger.info(
            'task_updated',
            extra={
                'task_id': task.pk,
                'condominium_id': task.condominium_id,
                'actor_user_id': user.pk if user else None,
                'operation': 'update',
            },
        )
        return task

    @staticmethod
    def validate_task_dates(release_date, estimated_completion_date, completion_date=None):
        if release_date and estimated_completion_date and estimated_completion_date < release_date:
            raise ValidationError(
                'A data prevista de conclusão não pode ser anterior à data de lançamento.'
            )
        if completion_date:
            if release_date and completion_date < release_date:
                raise ValidationError(
                    'A data de conclusão não pode ser anterior à data de lançamento.'
                )

    @staticmethod
    def validate_description(description):
        return validate_task_description(description)

    @staticmethod
    def get_admin_queryset():
        return Task.objects.select_related(
            'condominium', 'responsible_user', 'status',
        )
