import logging

from django.db import IntegrityError, transaction

from domains.parameters.repositories.assembly_status_repository import AssemblyStatusRepository
from domains.parameters.validators import ParametersValidator

logger = logging.getLogger(__name__)


class AssemblyStatusService:

    @staticmethod
    def normalize_description(description):
        if description is None:
            return None
        return description.strip()

    @staticmethod
    def validate_status_flags(data):
        if data.get('is_running') and AssemblyStatusRepository.running_exists():
            raise ValueError('Já existe um status marcado como "Em execução".')
        if data.get('is_complete') and AssemblyStatusRepository.complete_exists():
            raise ValueError('Já existe um status marcado como "Completo".')

    @staticmethod
    def _friendly_error(exc):
        message = str(exc)
        if 'unique_running_assembly_status' in message:
            return 'Já existe um status marcado como "Em execução".'
        if 'unique_complete_assembly_status' in message:
            return 'Já existe um status marcado como "Completo".'
        return 'Já existe um status de assembleia com este valor.'

    @staticmethod
    @transaction.atomic
    def create_assembly_status(data):
        data = dict(data)
        data['description'] = AssemblyStatusService.normalize_description(
            data.get('description')
        )
        ParametersValidator.validate_assembly_status(data)

        if AssemblyStatusRepository.description_exists(data['description']):
            raise ValueError('Já existe um status de assembleia com esta descrição.')

        AssemblyStatusService.validate_status_flags(data)

        try:
            assembly_status = AssemblyStatusRepository.create(data)
        except IntegrityError as exc:
            raise ValueError(AssemblyStatusService._friendly_error(exc))

        logger.info(
            'assembly_status_created',
            extra={
                'assembly_status_id': assembly_status.pk,
                'operation': 'create',
            },
        )
        return assembly_status

    @staticmethod
    @transaction.atomic
    def update_assembly_status(assembly_status, data):
        try:
            data = dict(data)
            if 'description' in data:
                data['description'] = AssemblyStatusService.normalize_description(
                    data.get('description')
                )
                if not data['description']:
                    raise ValueError('A descrição é obrigatória.')

                if AssemblyStatusRepository.description_exists(
                    data['description'], exclude_pk=assembly_status.pk
                ):
                    raise ValueError('Já existe um status de assembleia com esta descrição.')

            if data.get('is_running') and AssemblyStatusRepository.running_exists(
                exclude_pk=assembly_status.pk
            ):
                raise ValueError('Já existe um status marcado como "Em execução".')

            if data.get('is_complete') and AssemblyStatusRepository.complete_exists(
                exclude_pk=assembly_status.pk
            ):
                raise ValueError('Já existe um status marcado como "Completo".')

            updated = AssemblyStatusRepository.update(assembly_status, data)
        except IntegrityError as exc:
            raise ValueError(AssemblyStatusService._friendly_error(exc))

        logger.info(
            'assembly_status_updated',
            extra={
                'assembly_status_id': assembly_status.pk,
                'operation': 'update',
            },
        )
        return updated

    @staticmethod
    @transaction.atomic
    def delete_assembly_status(assembly_status):
        AssemblyStatusRepository.delete(assembly_status)
        logger.info(
            'assembly_status_deleted',
            extra={
                'assembly_status_id': assembly_status.pk,
                'operation': 'delete',
            },
        )

    @staticmethod
    @transaction.atomic
    def toggle_active(assembly_status, active):
        assembly_status.is_active = bool(active)
        assembly_status.save()
        logger.info(
            'assembly_status_status_changed',
            extra={
                'assembly_status_id': assembly_status.pk,
                'is_active': assembly_status.is_active,
                'operation': 'set_active',
            },
        )
        return assembly_status