from domains.administrative.models.bank_accounts import BankAccount


class BankAccountRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return BankAccount.objects.get(pk=id)
        except BankAccount.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return BankAccount.objects.select_related('bank', 'condominium', 'account_type').all()

    @staticmethod
    def create(data):
        account = BankAccount(**data)
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
