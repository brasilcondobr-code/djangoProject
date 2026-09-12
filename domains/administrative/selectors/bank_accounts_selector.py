from domains.administrative.models.bank_accounts import BankAccount


class BankAccountSelector:
    @staticmethod
    def get_all():
        return BankAccount.objects.select_related('bank', 'condominium', 'account_type').all()

    @staticmethod
    def get_by_id(id):
        try:
            return BankAccount.objects.select_related('bank', 'condominium', 'account_type').get(pk=id)
        except BankAccount.DoesNotExist:
            return None

    @staticmethod
    def get_by_bank_and_agency(bank, agency):
        return BankAccount.objects.filter(bank=bank, agency=agency).select_related('bank', 'condominium', 'account_type').all()
