from django.db import transaction
from domains.administrative.models.chart_of_account import ChartOfAccount
from django.db.models import Q


class ChartOfAccountRepository:

    @staticmethod
    def get_by_id(account_id):
        try:
            return ChartOfAccount.objects.get(pk=account_id)
        except ChartOfAccount.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return ChartOfAccount.objects.select_related(
            'condominium', 'account_type', 'account_class',
            'account_group', 'account_subgroup',
            'parent_account', 'status',
        ).all()

    @staticmethod
    def list_by_condominium(condominium_id):
        return ChartOfAccount.objects.filter(
            condominium_id=condominium_id,
        ).select_related(
            'account_type', 'account_class',
            'account_group', 'account_subgroup', 'status',
        ).all()

    @staticmethod
    def list_parent_candidates(account, condominium_id):
        qs = ChartOfAccount.objects.filter(
            condominium_id=condominium_id,
        )
        if account.pk:
            qs = qs.exclude(pk=account.pk).exclude(
                Q(parent_account=account) | Q(pk__in=account.child_accounts.values('pk'))
            )
        return qs

    @staticmethod
    def create(data):
        account = ChartOfAccount(**data)
        account.save()
        return account

    @staticmethod
    def update(account, data):
        for key, value in data.items():
            setattr(account, key, value)
        account.save()
        return account

    @staticmethod
    def delete(account):
        account.delete()

    @staticmethod
    def exists_with_code(condominium_id, account_code, exclude_pk=None):
        qs = ChartOfAccount.objects.filter(
            condominium_id=condominium_id,
            account_code=account_code,
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()
