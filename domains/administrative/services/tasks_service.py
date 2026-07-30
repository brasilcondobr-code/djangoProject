import logging

from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from domains.administrative.models.task import Task
from domains.administrative.models.task_history import TaskHistory
from domains.administrative.validators import validate_task_title, validate_task_description
from domains.email_service.models import ConnectionStatus

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
        if not TaskService.can_manage_task(user, task):
            raise PermissionDenied('Você não tem permissão para editar esta tarefa.')
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
    @transaction.atomic
    def delete_task(user, task):
        if not TaskService.can_manage_task(user, task):
            raise PermissionDenied('Você não tem permissão para excluir esta tarefa.')
        task.delete()
        logger.info(
            'task_deleted',
            extra={
                'task_id': task.pk,
                'actor_user_id': user.pk if user else None,
                'operation': 'delete',
            },
        )

    @staticmethod
    @transaction.atomic
    def add_task_history(user, task, validated_data):
        if not TaskService.can_add_history(user, task):
            raise PermissionDenied(
                'Você não tem permissão para adicionar histórico a esta tarefa.'
            )
        validated_data['task'] = task
        validated_data['created_by_user'] = user
        history = TaskHistory.objects.create(**validated_data)
        logger.info(
            'task_history_created',
            extra={
                'history_id': history.pk,
                'task_id': task.pk,
                'actor_user_id': user.pk if user else None,
                'operation': 'add_history',
            },
        )
        return history

    @staticmethod
    def can_manage_task(user, task):
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return task.created_by_user == user

    @staticmethod
    def can_add_history(user, task):
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if task.created_by_user == user:
            return True
        if task.responsible_user == user:
            return True
        return False

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

    @staticmethod
    @transaction.atomic
    def bulk_update_status(user, task_ids, new_status_id):
        if not new_status_id:
            raise ValidationError('Informe o novo status.')
        try:
            new_status = ConnectionStatus.objects.get(pk=new_status_id, is_active=True)
        except ConnectionStatus.DoesNotExist:
            raise ValidationError('O status informado é inválido ou está inativo.')

        tasks = Task.objects.filter(pk__in=task_ids).select_related('status')
        allowed_ids = []
        denied = []
        for task in tasks:
            if TaskService.can_manage_task(user, task):
                allowed_ids.append(task.pk)
            else:
                denied.append(task.pk)

        if not allowed_ids:
            raise ValidationError(
                'Nenhuma tarefa selecionada pertence ao usuário atual.'
            )

        if denied:
            raise ValidationError(
                f'{len(denied)} tarefa(s) não pertence(m) ao usuário atual. '
                'Operação cancelada.'
            )

        updated = Task.objects.filter(pk__in=allowed_ids).update(status=new_status)
        logger.info(
            'task_status_bulk_updated',
            extra={
                'actor_user_id': user.pk if user else None,
                'affected_count': updated,
                'status_id': new_status_id,
                'operation': 'bulk_update_status',
            },
        )
        return updated

    @staticmethod
    @transaction.atomic
    def bulk_complete_tasks(user, task_ids, completion_date_str, new_status_id):
        from datetime import date, datetime

        if not task_ids:
            raise ValidationError('Nenhuma tarefa selecionada.')
        if not completion_date_str:
            raise ValidationError('Informe a data efetiva de conclusão.')
        if not new_status_id:
            raise ValidationError('Informe o novo status.')

        try:
            completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            raise ValidationError('Formato de data inválido. Use o formato dd/mm/aaaa.')

        try:
            new_status = ConnectionStatus.objects.get(pk=new_status_id, is_active=True)
        except ConnectionStatus.DoesNotExist:
            raise ValidationError('O status informado é inválido ou está inativo.')

        tasks = Task.objects.filter(pk__in=task_ids).select_related('status')
        allowed_ids = []
        denied = []
        for task in tasks:
            if TaskService.can_manage_task(user, task):
                if task.release_date and completion_date < task.release_date:
                    raise ValidationError(
                        f'A data de conclusão ({completion_date}) não pode ser '
                        f'anterior à data de lançamento ({task.release_date}) '
                        f'da tarefa "{task.title}".'
                    )
                allowed_ids.append(task.pk)
            else:
                denied.append(task.pk)

        if not allowed_ids:
            raise ValidationError(
                'Nenhuma tarefa selecionada pertence ao usuário atual.'
            )

        if denied:
            raise ValidationError(
                f'{len(denied)} tarefa(s) não pertence(m) ao usuário atual. '
                'Operação cancelada.'
            )

        updated = Task.objects.filter(pk__in=allowed_ids).update(
            completion_date=completion_date,
            status=new_status,
        )
        logger.info(
            'task_bulk_completed',
            extra={
                'actor_user_id': user.pk if user else None,
                'affected_count': updated,
                'completion_date': str(completion_date),
                'status_id': new_status_id,
                'operation': 'bulk_complete_tasks',
            },
        )
        return updated
