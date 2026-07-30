import logging
from django.db import transaction
from django.db.models import Q
from domains.administrative.repositories.chartofaccount_repository import ChartOfAccountRepository
from domains.administrative.selectors.chartofaccount_selector import ChartOfAccountSelector
from domains.administrative.validators import validate_chart_account_code, validate_external_reference, validate_archive_reason
from domains.parameters.models import Accountingclasstypes, ChartofaccountsMaingroup, ChartofaccountsSubgroup

logger = logging.getLogger(__name__)


def _detect_cycle(account, parent_account):
    if parent_account is None:
        return False
    current = parent_account
    visited = {account.pk}
    while current is not None:
        if current.pk in visited:
            return True
        visited.add(current.pk)
        current = current.parent_account
    return False


class ChartOfAccountService:

    @staticmethod
    def create_chart_of_account(data, user=None):
        validate_chart_account_code(data.get('account_code', ''))
        validate_external_reference(data.get('external_reference', ''))
        validate_archive_reason(data.get('archive_reason', ''))

        condominium_id = data.get('condominium_id') or getattr(data.get('condominium'), 'pk', None)
        account_code = data.get('account_code', '').strip()

        if not condominium_id:
            raise ValueError('Condomínio é obrigatório.')

        if ChartOfAccountRepository.exists_with_code(condominium_id, account_code):
            raise ValueError('Já existe uma conta com este código para este condomínio.')

        parent = data.get('parent_account')
        if parent is not None:
            parent_id = parent.pk if hasattr(parent, 'pk') else parent
            try:
                parent_obj = ChartOfAccountSelector.get_by_id(int(parent_id))
            except (ValueError, TypeError):
                parent_obj = None
            if parent_obj is None:
                raise ValueError('Conta-pai não encontrada.')
            if parent_obj.condominium_id != condominium_id:
                raise ValueError('A conta-pai deve pertencer ao mesmo condomínio.')
            parent_level = int(parent_obj.account_level)
            new_level = int(data.get('account_level', 0))
            if parent_level + 1 != new_level:
                raise ValueError(
                    f'O nível da conta-filho deve ser {parent_level + 1} '
                    f'(nível da conta-pai mais 1).'
                )
            data['account_level'] = new_level

        replacement = data.get('replacement_account')
        if replacement is not None:
            replacement_id = replacement.pk if hasattr(replacement, 'pk') else replacement
            try:
                replacement_obj = ChartOfAccountSelector.get_by_id(int(replacement_id))
            except (ValueError, TypeError):
                replacement_obj = None
            if replacement_obj is None:
                raise ValueError('Conta substituta não encontrada.')
            if replacement_obj.condominium_id != condominium_id:
                raise ValueError('A conta substituta deve pertencer ao mesmo condomínio.')
            if replacement_obj.pk == data.get('pk'):
                raise ValueError('A conta substituta não pode ser a própria conta.')

        try:
            with transaction.atomic():
                creation_data = {k: v for k, v in data.items() if k != 'pk'}
                if user and user.is_authenticated:
                    creation_data['created_by'] = user
                account = ChartOfAccountRepository.create(creation_data)
                logger.info(
                    'chart_of_account.created',
                    extra={
                        'account_id': account.pk,
                        'condominium_id': condominium_id,
                        'user_id': getattr(user, 'pk', None),
                        'operation': 'create',
                        'status': 'success',
                    },
                )
                return account
        except Exception as e:
            logger.error(
                'chart_of_account.create_error',
                extra={
                    'condominium_id': condominium_id,
                    'error': str(e),
                    'operation': 'create',
                    'status': 'error',
                },
            )
            raise

    @staticmethod
    def update_chart_of_account(account_id, data, user=None):
        account = ChartOfAccountSelector.get_by_id(account_id)
        if account is None:
            return None

        account_code = data.get('account_code', account.account_code)
        if account_code:
            validate_chart_account_code(account_code)
            account_code = account_code.strip()
            if account_code != account.account_code:
                if ChartOfAccountRepository.exists_with_code(
                    account.condominium_id, account_code, exclude_pk=account.pk,
                ):
                    raise ValueError('Já existe uma conta com este código para este condomínio.')

        validate_external_reference(data.get('external_reference', ''))
        validate_archive_reason(data.get('archive_reason', ''))

        parent = data.get('parent_account')
        if parent is not None:
            parent_id = parent.pk if hasattr(parent, 'pk') else parent
            parent_obj = ChartOfAccountSelector.get_by_id(int(parent_id))
            if parent_obj is None:
                raise ValueError('Conta-pai não encontrada.')
            if parent_obj.condominium_id != account.condominium_id:
                raise ValueError('A conta-pai deve pertencer ao mesmo condomínio.')
            if parent_obj.pk == account.pk:
                raise ValueError('A conta não pode ser pai dela mesma.')
            if _detect_cycle(account, parent_obj):
                raise ValueError('Foi detectado um ciclo na hierarquia de contas.')
            new_level = int(parent_obj.account_level) + 1
            data['account_level'] = new_level

        replacement = data.get('replacement_account')
        if replacement is not None:
            replacement_id = replacement.pk if hasattr(replacement, 'pk') else replacement
            try:
                replacement_obj = ChartOfAccountSelector.get_by_id(int(replacement_id))
            except (ValueError, TypeError):
                replacement_obj = None
            if replacement_obj is None:
                raise ValueError('Conta substituta não encontrada.')
            if replacement_obj.condominium_id != account.condominium_id:
                raise ValueError('A conta substituta deve pertencer ao mesmo condomínio.')
            if replacement_obj.pk == account.pk:
                raise ValueError('A conta substituta não pode ser a própria conta.')

        try:
            with transaction.atomic():
                update_data = {k: v for k, v in data.items() if k != 'pk'}
                if user and user.is_authenticated:
                    update_data['updated_by'] = user
                account = ChartOfAccountRepository.update(account, update_data)
                logger.info(
                    'chart_of_account.updated',
                    extra={
                        'account_id': account.pk,
                        'condominium_id': account.condominium_id,
                        'user_id': getattr(user, 'pk', None),
                        'operation': 'update',
                        'status': 'success',
                    },
                )
                return account
        except Exception as e:
            logger.error(
                'chart_of_account.update_error',
                extra={
                    'account_id': account_id,
                    'error': str(e),
                    'operation': 'update',
                    'status': 'error',
                },
            )
            raise

    @staticmethod
    def delete_chart_of_account(account_id):
        account = ChartOfAccountSelector.get_by_id(account_id)
        if account is None:
            return False
        if account.is_system_account:
            raise ValueError('Contas do sistema não podem ser excluídas.')
        if account.child_accounts.exists():
            raise ValueError('Não é possível excluir uma conta que possui contas-filhas.')
        logger.info(
            'chart_of_account.deleted',
            extra={
                'account_id': account.pk,
                'condominium_id': account.condominium_id,
                'operation': 'delete',
                'status': 'success',
            },
        )
        ChartOfAccountRepository.delete(account)
        return True

    @staticmethod
    def get_all_chart_of_accounts():
        return ChartOfAccountSelector.get_all()

    @staticmethod
    def get_chart_of_account_by_id(account_id):
        return ChartOfAccountSelector.get_by_id(account_id)

    @staticmethod
    def get_classes_by_type(tipo_conta_id):
        if not tipo_conta_id:
            return []
        try:
            tipo_conta_id = int(tipo_conta_id)
        except (ValueError, TypeError):
            return []
        return list(
            Accountingclasstypes.objects.filter(
                account_type_id=tipo_conta_id, is_active=True,
            ).select_related('account_type').order_by('description').values(
                'id', 'code', 'description', 'account_type__description',
            )
        )

    @staticmethod
    def get_groups_by_class(classe_contabil_id):
        if not classe_contabil_id:
            return []
        try:
            classe_contabil_id = int(classe_contabil_id)
        except (ValueError, TypeError):
            return []
        return list(
            ChartofaccountsMaingroup.objects.filter(
                account_class_id=classe_contabil_id, is_active=True,
            ).select_related('account_class').order_by('description').values(
                'id', 'code', 'description',
                'account_class__code', 'account_class__description',
                'account_class__account_type__description',
            )
        )

    @staticmethod
    def get_subgroups_by_group(grupo_principal_id):
        if not grupo_principal_id:
            return []
        try:
            grupo_principal_id = int(grupo_principal_id)
        except (ValueError, TypeError):
            return []
        return list(
            ChartofaccountsSubgroup.objects.filter(
                main_group_id=grupo_principal_id, is_active=True,
            ).select_related('main_group').order_by('description').values(
                'id', 'code', 'description',
                'main_group__code', 'main_group__description',
                'main_group__account_class__description',
            )
        )
