from domains.administrative.models.chart_of_account import ChartOfAccount


class ChartOfAccountSelector:

    @staticmethod
    def get_all():
        return ChartOfAccount.objects.select_related(
            'condominium', 'account_type', 'account_class',
            'account_group', 'account_subgroup',
            'parent_account', 'status',
        ).all()

    @staticmethod
    def get_by_id(account_id):
        try:
            return ChartOfAccount.objects.select_related(
                'condominium', 'account_type', 'account_class',
                'account_group', 'account_subgroup',
                'parent_account', 'status',
                'replacement_account',
            ).get(pk=account_id)
        except ChartOfAccount.DoesNotExist:
            return None

    @staticmethod
    def get_children(account_id):
        return ChartOfAccount.objects.filter(parent_account_id=account_id)

    @staticmethod
    def get_by_condominium(condominium_id):
        return ChartOfAccount.objects.filter(
            condominium_id=condominium_id,
        ).select_related(
            'account_type', 'account_class', 'status',
        ).all()
